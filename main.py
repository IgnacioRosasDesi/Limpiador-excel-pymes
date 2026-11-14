import io
import zipfile
from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from auth_db import (
    eliminar_preset_usuario,
    guardar_historial_limpieza,
    guardar_preset_usuario,
    iniciar_sesion,
    obtener_historial_usuario,
    obtener_perfil_usuario,
    obtener_presets_usuario,
    registrar_usuario,
)
from generador_pdf import generar_reporte_pdf
from motor_limpieza import leer_archivo, limpiar_dataframe
from pagos import generar_link_mercadopago

app = FastAPI(
    title="RowRescue API",
    description="Backend SaaS de estandarización y limpieza de datos",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def estado_servidor():
    return {"estado": "Servidor RowRescue en línea 🚀"}


# --- AUTENTICACIÓN Y PERFIL ---
@app.post("/api/registro")
def registro(email: str = Form(...), password: str = Form(...)):
    res = registrar_usuario(email, password)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"].get("message", "Error al registrar"))
    obtener_perfil_usuario(email)
    return {"mensaje": "Usuario registrado con éxito", "email": res["email"]}


@app.post("/api/login")
def login(email: str = Form(...), password: str = Form(...)):
    res = iniciar_sesion(email, password)
    if "error" in res:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas o usuario no existe.")
    perfil = obtener_perfil_usuario(res["email"])
    return {
        "mensaje": "Login exitoso",
        "usuario": {
            "email": res["email"],
            "uid": res["uid"],
            "plan": perfil.get("plan", "free"),
        },
    }


@app.get("/api/historial/{email}")
def ver_historial(email: str):
    return {"historial": obtener_historial_usuario(email)}


# --- PRESETS DE CONFIGURACIÓN ---
@app.get("/api/presets/{email}")
def listar_presets(email: str):
    return {"presets": obtener_presets_usuario(email)}


@app.post("/api/presets")
def crear_preset(
    email: str = Form(...),
    nombre_preset: str = Form(...),
    columna: str = Form(""),
    texto_basura: str = Form(""),
):
    exito = guardar_preset_usuario(email, nombre_preset, columna, texto_basura)
    if not exito:
        raise HTTPException(status_code=500, detail="No se pudo guardar el preset")
    return {"mensaje": "Preset guardado con éxito"}


@app.delete("/api/presets/{email}/{nombre_preset}")
def borrar_preset(email: str, nombre_preset: str):
    exito = eliminar_preset_usuario(email, nombre_preset)
    if not exito:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el preset")
    return {"mensaje": "Preset eliminado"}


# --- MOTOR DE LIMPIEZA + REPORTE PDF ---
@app.post("/api/limpiar")
async def procesar_archivos(
    email: Annotated[str, Form()],
    archivos: Annotated[list[UploadFile], File()],
    columna_duplicados: Annotated[str | None, Form()] = None,
    texto_basura: Annotated[str | None, Form()] = None,
):
    perfil = obtener_perfil_usuario(email)
    plan = perfil.get("plan", "free")

    if plan == "free" and len(archivos) > 1:
        raise HTTPException(
            status_code=403,
            detail="El plan Gratuito permite 1 archivo por vez. Actualiza a Premium para lotes masivos.",
        )

    zip_buffer = io.BytesIO()
    stats_acumuladas = {"originales": 0, "duplicados": 0, "vacias": 0, "basura": 0}

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for archivo in archivos:
            contenido = await archivo.read()
            buffer_entrada = io.BytesIO(contenido)
            buffer_entrada.name = archivo.filename

            try:
                df = leer_archivo(buffer_entrada)
                df_limpio, stats = limpiar_dataframe(
                    df,
                    columna_duplicados=columna_duplicados if columna_duplicados else None,
                    valor_basura=texto_basura if texto_basura else None,
                )

                stats_acumuladas["originales"] += stats.get("filas_originales", 0)
                stats_acumuladas["duplicados"] += stats.get("duplicados_eliminados", 0)
                stats_acumuladas["vacias"] += stats.get("filas_vacias_eliminadas", 0)
                stats_acumuladas["basura"] += stats.get("filas_basura_eliminadas", 0)

                excel_buffer = io.BytesIO()
                df_limpio.to_excel(excel_buffer, index=False)
                nombre_limpio = f"limpio_{archivo.filename.rsplit('.', 1)[0]}.xlsx"
                zip_file.writestr(nombre_limpio, excel_buffer.getvalue())

            except Exception as e: 
                raise HTTPException(
                    status_code=400, 
                    detail=f"Error procesando {archivo.filename}: {e!s}",
                    ) from e

    # Incluimos el reporte PDF directamente dentro del ZIP descargable
    pdf_bytes = generar_reporte_pdf(email, len(archivos), stats_acumuladas)
    zip_file.writestr("Reporte_Limpieza_RowRescue.pdf", pdf_bytes)

    guardar_historial_limpieza(email, len(archivos), stats_acumuladas)
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=RowRescue_Limpios.zip"},
    )


# --- PAGOS MERCADO PAGO ---
@app.post("/api/checkout")
def crear_checkout(email: str = Form(...), url_retorno: str = Form("http://localhost:5173")):
    url_pago = generar_link_mercadopago(email, url_retorno)
    if not url_pago:
        raise HTTPException(status_code=500, detail="No se pudo generar el enlace de Mercado Pago")
    return {"checkout_url": url_pago}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)