# 1. Imports nativos
import zipfile
from datetime import datetime
from io import BytesIO

# 2. Imports de terceros
import pandas as pd
import streamlit as st

# Importamos todas las funciones de Firebase (Auth, Firestore Historial y Presets)
from auth_db import (
    actualizar_plan_usuario,
    # ... (tus otros imports de auth_db)
    eliminar_preset_usuario,
    enviar_correo_verificacion,
    enviar_recuperacion_clave,
    guardar_historial_limpieza,
    guardar_preset_usuario,
    iniciar_sesion,
    obtener_historial_usuario,
    obtener_perfil_usuario,
    obtener_presets_usuario,
    registrar_usuario,
)
from generador_pdf import generar_reporte_pdf

# 3. Imports locales
from motor_limpieza import leer_archivo, limpiar_dataframe
from pagos import generar_link_mercadopago

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="RowRescue | Data Standardization", 
    page_icon="⚡", 
    layout="centered"
)

# --- INYECCIÓN DE CSS PARA BRANDING ---
estilo_oculto = """
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
"""
st.markdown(estilo_oculto, unsafe_allow_html=True)

# --- INICIALIZAR ESTADO DE SESIÓN ---
if 'usuario_autenticado' not in st.session_state:
    st.session_state['usuario_autenticado'] = False
if 'usuario_email' not in st.session_state:
    st.session_state['usuario_email'] = ""
if 'mostrar_login' not in st.session_state:
    st.session_state['mostrar_login'] = False

# =========================================================
# PANTALLA PÚBLICA / LANDING PAGE O LOGIN (SI NO ESTÁ AUTENTICADO)
# =========================================================
if not st.session_state['usuario_autenticado']:
    
    if st.session_state['mostrar_login']:
        if st.button("← Volver a la presentación"):
            st.session_state['mostrar_login'] = False
            st.rerun()
            
        st.markdown("<h1 style='text-align: center; color: #3b82f6;'>⚡ RowRescue</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8;'>Acceso a la plataforma de DesiLabs</p>", unsafe_allow_html=True)
        st.write("")
        
        tab_login, tab_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
        
        with tab_login:
            email_login = st.text_input("Correo electrónico", key="log_email")
            pass_login = st.text_input("Contraseña", type="password", key="log_pass")
            
            if st.button("Entrar a la Plataforma", type="primary", use_container_width=True):
                if email_login and pass_login:
                    with st.spinner("Autenticando..."):
                        res = iniciar_sesion(email_login, pass_login)
                        if "error" in res:
                            st.error("Credenciales incorrectas o el usuario no existe.")
                        else:
                            st.session_state['usuario_autenticado'] = True
                            st.session_state['usuario_email'] = res['email']
                            st.rerun() 
                else:
                    st.warning("Por favor ingresa tu correo y contraseña.")
            
            with st.expander("¿Olvidaste tu contraseña?"):
                st.write("Ingresa tu correo para recibir un enlace seguro de recuperación.")
                email_recuperacion = st.text_input("Tu correo electrónico registrado", key="recuperacion")
                
                if st.button("Enviar enlace de recuperación", use_container_width=True):
                    if email_recuperacion:
                        with st.spinner("Verificando..."):
                            res_recup = enviar_recuperacion_clave(email_recuperacion)
                            if "error" not in res_recup:
                                st.success("✅ Si el correo existe en DesiLabs, recibirás instrucciones en unos minutos.")
                            else:
                                st.error("Ocurrió un error al intentar enviar el correo. Revisa que el formato sea correcto.")
                    else:
                        st.warning("Por favor, ingresa un correo válido.")
                    
        with tab_registro:
            email_reg = st.text_input("Correo electrónico", key="reg_email")
            pass_reg = st.text_input("Contraseña (mín. 6 caracteres)", type="password", key="reg_pass")
            pass_reg_conf = st.text_input("Confirmar Contraseña", type="password", key="reg_pass_conf")
            
            if st.button("Crear Cuenta Gratuita", type="primary", use_container_width=True):
                if pass_reg != pass_reg_conf:
                    st.error("Las contraseñas no coinciden.")
                elif len(pass_reg) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                elif email_reg and pass_reg:
                    with st.spinner("Creando cuenta y validando..."):
                        res = registrar_usuario(email_reg, pass_reg)
                        
                        if "error" in res:
                            st.error(f"Error al registrar: {res['error'].get('message', 'Correo inválido o en uso.')}")
                        else:
                            id_token = res.get("idToken")
                            if id_token:
                                verif_res = enviar_correo_verificacion(id_token)
                                if "error" not in verif_res:
                                    st.success("✅ ¡Cuenta creada exitosamente! Hemos enviado un enlace de seguridad a tu correo para verificar tu identidad.")
                                else:
                                    st.warning("✅ Cuenta creada, pero hubo un problema enviando el correo de verificación.")
                            else:
                                st.success("✅ ¡Cuenta creada exitosamente! Ahora ve a la pestaña 'Iniciar Sesión' para entrar.")
                else:
                    st.warning("Completa todos los campos.")
                    
    else:
        col_top1, col_top2 = st.columns([4, 2])
        with col_top2:
            if st.button("🔑 Iniciar Sesión", type="secondary", use_container_width=True):
                st.session_state['mostrar_login'] = True
                st.rerun()

        st.markdown("<h1 style='text-align: center; color: #3b82f6;'>⚡ RowRescue</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>La plataforma inteligente para estandarizar y limpiar tus bases de datos</h3>", unsafe_allow_html=True)
        st.write("")
        st.markdown(
            "<p style='text-align: center; color: #94a3b8; font-size: 1.1rem;'>"
            "Optimiza tus planillas de Excel y CSV en segundos. Elimina duplicados masivos, filtra datos "
            "indeseados y descarga tus reportes listos para la toma de decisiones."
            "</p>", 
            unsafe_allow_html=True
        )
        st.write("")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🚀 Probar Plataforma Gratis", type="primary", use_container_width=True):
                st.session_state['mostrar_login'] = True
                st.rerun()
                
        st.divider()
        
        st.subheader("💡 ¿Por qué elegir RowRescue?")
        
        col_feat1, col_feat2, col_feat3 = st.columns(3)
        with col_feat1:
            st.markdown("### 📁 Masivo")
            st.write("Sube múltiples archivos a la vez y recíbelos limpios en un archivo `.zip` organizado.")
        with col_feat2:
            st.markdown("### 🔍 Preciso")
            st.write("Elimina filas duplicadas por columna o detecta textos basura en toda la base de datos.")
        with col_feat3:
            st.markdown("### 📈 Visual")
            st.write("Analiza gráficos de impacto en tiempo real con la proporción exacta de datos rescatados.")

# =========================================================
# APLICACIÓN PRINCIPAL ROWRESCUE (SI ESTÁ AUTENTICADO)
# =========================================================
else:
    # --- BARRA SUPERIOR DE USUARIO ---
    col_vacia, col_user, col_logout = st.columns([3, 4, 2])
    with col_user:
        st.markdown(f"<div style='text-align: right; padding-top: 8px; color: #94a3b8;'>👤 {st.session_state['usuario_email']}</div>", unsafe_allow_html=True)
    with col_logout:
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state['usuario_autenticado'] = False
            st.session_state['usuario_email'] = ""
            st.session_state['mostrar_login'] = False
            st.rerun()
            
    st.divider()

    # --- CABECERA DE LA APP ---
    col_logo, col_texto = st.columns([1, 6])
    with col_logo:
        st.markdown("<h1 style='text-align: center; color: #3b82f6;'>⚡</h1>", unsafe_allow_html=True)
    with col_texto:
        st.markdown("<h1 style='margin-bottom: 0px;'>RowRescue</h1>", unsafe_allow_html=True)

    st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>Plataforma inteligente de estandarización y limpieza de bases de datos.</p>", unsafe_allow_html=True)
    st.divider()

    # --- VERIFICACIÓN DE PAGOS DESDE MERCADO PAGO ---
    # Si Mercado Pago redirige de vuelta con éxito, la URL tendrá ?pago=exitoso
    query_params = st.query_params
    if query_params.get("pago") == "exitoso":
        # ¡El usuario acaba de pagar! Lo ascendemos a Premium en Firestore
        actualizar_plan_usuario(st.session_state['usuario_email'], "premium")
        st.success("🎉 ¡Pago confirmado! Bienvenido a RowRescue Premium. Disfruta de limpieza masiva sin límites.")
        # Limpiamos la URL para que no vuelva a procesarse al recargar
        st.query_params.clear()

    # --- OBTENER PERFIL Y PLAN DEL USUARIO ---
    perfil = obtener_perfil_usuario(st.session_state['usuario_email'])
    plan_actual = perfil.get("plan", "free")

    if plan_actual == "free":
        st.info("💡 **Plan Gratuito Activo:** Puedes procesar 1 archivo a la vez.")
        
        with st.expander("⭐ Actualizar a Premium ($5.000 CLP / de por vida)"):
            st.write("Desbloquea procesamiento masivo ilimitado para múltiples archivos simultáneos.")
            # Para Streamlit Cloud, la URL base es la de tu app. En local es localhost:8501
            url_base = "https://rowrescue.streamlit.app/" 
            link_pago = generar_link_mercadopago(st.session_state['usuario_email'], url_base)
            
            if link_pago:
                st.link_button("💳 Pagar de forma segura con Mercado Pago", link_pago, type="primary")
            else:
                st.error("El sistema de pagos se está configurando. Vuelve más tarde.")
    else:
        st.success("⭐ **Plan Premium Activo:** Procesamiento masivo ilimitado desbloqueado.")

    # --- SECCIÓN DE HISTORIAL RECIENTE (FIRESTORE) ---
    with st.expander("📜 Ver mi historial de actividad reciente"):
        historial_usuario = obtener_historial_usuario(st.session_state['usuario_email'])
        if historial_usuario:
            for h in historial_usuario:
                try:
                    dt = datetime.fromisoformat(h.get("fecha", ""))
                    fecha_str = dt.strftime("%d-%m-%Y %H:%M")
                except Exception:  # noqa: BLE001
                    fecha_str = "Reciente"
                
                st.markdown(f"- **{fecha_str}** — 📁 {h.get('num_archivos', 1)} archivo(s) procesados | 🗑️ {h.get('duplicados_eliminados', 0) + h.get('vacias_eliminadas', 0) + h.get('basura_eliminada', 0)} elementos eliminados en total.")
        else:
            st.info("Aún no tienes registros de limpiezas pasadas. ¡Sube tu primer archivo abajo!")

    st.divider()

    # --- LÓGICA PRINCIPAL DE LIMPIEZA MÚLTIPLE ---
# --- LÓGICA PRINCIPAL DE LIMPIEZA MÚLTIPLE ---
    archivos_subidos = st.file_uploader(
        "Arrastra uno o múltiples archivos aquí (.xlsx, .csv)", 
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        help="💡 Puedes subir varios archivos a la vez (Máximo 50 MB por archivo)."
    )

    # --- RESTRICCIÓN FREEMIUM ---
    if archivos_subidos and plan_actual == "free" and len(archivos_subidos) > 1:
        st.error("🔒 **Límite del Plan Gratuito excedido.** Solo puedes procesar 1 archivo a la vez. Actualiza a Premium para procesar múltiples archivos simultáneamente.")
        st.stop() # Detiene la ejecución para que no limpie los archivos

    if archivos_subidos:
        # Límite de tamaño seguro en Bytes (50 Megabytes)
        LIMITE_TAMANO_MB = 50
        LIMITE_BYTES = LIMITE_TAMANO_MB * 1024 * 1024
        
        # Validar si algún archivo supera el límite permitido
        archivos_validos = []
        demasiado_pesados = []
        
        for archivo in archivos_subidos:
            if archivo.size > LIMITE_BYTES:
                demasiado_pesados.append(archivo.name)
            else:
                archivos_validos.append(archivo)
                
        if demasiado_pesados:
            st.error(f"❌ Los siguientes archivos superan el límite de {LIMITE_TAMANO_MB}MB permitidos: {', '.join(demasiado_pesados)}. Por favor, sube archivos más livianos para proteger la memoria del sistema.")
        
        if archivos_validos:
            if demasiado_pesados:
                st.info("ℹ️ Procesando únicamente los archivos que cumplen con el límite de tamaño.")
                
            try:
                df_ejemplo = leer_archivo(archivos_validos[0])
                
                # --- CARGAR PRESETS GUARDADOS ---
                presets_disponibles = obtener_presets_usuario(st.session_state['usuario_email'])
                nombres_presets = ["-- Personalizado (Sin preset) --"] + [p["nombre_preset"] for p in presets_disponibles]
                
                st.subheader("⚙️ Opciones de Limpieza Masiva")
                
                preset_seleccionado = st.selectbox("📂 Cargar Preset Guardado", nombres_presets)
                
                # Valores por defecto según preset seleccionado
                def_columna = "Fila exacta (Todas las columnas)"
                def_texto = ""
                
                if preset_seleccionado != "-- Personalizado (Sin preset) --":
                    for p in presets_disponibles:
                        if p["nombre_preset"] == preset_seleccionado:
                            def_columna = p["columna"]
                            def_texto = p["texto_basura"]
                    st.info(f"✨ Preset '{preset_seleccionado}' cargado correctamente.")

                opciones_dup = ["Fila exacta (Todas las columnas)"] + list(df_ejemplo.columns)
                
                index_col = 0
                if def_columna in opciones_dup:
                    index_col = opciones_dup.index(def_columna)
                    
                columna_seleccionada = st.selectbox(
                    "Identificar registros duplicados basándose en:",
                    opciones_dup,
                    index=index_col
                )
                
                st.markdown("### 🔍 Filtro de Datos Específicos")
                valor_buscado = st.text_input(
                    "¿Hay alguna palabra o dato que desees borrar de tu base de datos? (Ej: 'Prueba', 'Cancelado')", 
                    value=def_texto,
                    placeholder="Escribe aquí para buscar..."
                )
                
                with st.expander("💾 Guardar o gestionar esta configuración como Preset"):
                    nuevo_nombre_preset = st.text_input("Nombre para este preset (Ej: 'Limpieza Clientes Mensual')")
                    col_btn_save, col_btn_del = st.columns(2)
                    
                    with col_btn_save:
                        if st.button("Guardar Configuración"):
                            if nuevo_nombre_preset:
                                ok = guardar_preset_usuario(
                                    st.session_state['usuario_email'], 
                                    nuevo_nombre_preset, 
                                    columna_seleccionada, 
                                    valor_buscado
                                )
                                if ok:
                                    st.success(f"Preset '{nuevo_nombre_preset}' guardado con éxito.")
                                    st.rerun()
                                else:
                                    st.error("Error al guardar el preset.")
                            else:
                                st.warning("Ingresa un nombre para el preset.")
                                
                    with col_btn_del:
                        if presets_disponibles and preset_seleccionado != "-- Personalizado (Sin preset) --" and st.button("🗑️ Borrar preset actual"):
                            eliminar_preset_usuario(st.session_state['usuario_email'], preset_seleccionado)
                            st.success("Preset eliminado.")
                            st.rerun()

                confirmar_basura = False
                if valor_buscado:
                     confirmar_basura = st.checkbox(
                            f"🚨 Confirmo que deseo ELIMINAR todas las filas que contengan '{valor_buscado}' en TODOS mis archivos.",
                            help="Atención: Esta eliminación ocurrirá en todos los documentos que hayas subido."
                        )
                
                st.divider()

                if st.button("✨ Procesar Archivos", type="primary", use_container_width=True):
                    with st.spinner(f"Limpiando {len(archivos_validos)} archivo(s)... esto puede tomar un momento."):
                        
                        clave = None if columna_seleccionada == "Fila exacta (Todas las columnas)" else columna_seleccionada
                        texto_a_borrar = valor_buscado if confirmar_basura else None
                        
                        zip_buffer = BytesIO()
                        
                        total_originales = 0
                        total_duplicados = 0
                        total_vacias = 0
                        total_basura = 0
                        
                        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                            for archivo in archivos_validos:
                                df_raw = leer_archivo(archivo)
                                df_limpio, stats = limpiar_dataframe(df_raw, columna_duplicados=clave, valor_basura=texto_a_borrar)
                                
                                total_originales += stats['filas_originales']
                                total_duplicados += stats['duplicados_eliminados']
                                total_vacias += stats['filas_vacias_eliminadas']
                                total_basura += stats['filas_basura_eliminadas']
                                
                                excel_buffer = BytesIO()
                                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                    df_limpio.to_excel(writer, index=False, sheet_name='Limpio')
                                
                                nombre_archivo_limpio = f"limpio_{archivo.name.rsplit('.', 1)[0]}.xlsx"
                                zip_file.writestr(nombre_archivo_limpio, excel_buffer.getvalue())
                        
                        stats_globales = {
                            "originales": total_originales,
                            "duplicados": total_duplicados,
                            "vacias": total_vacias,
                            "basura": total_basura
                        }
                        guardar_historial_limpieza(st.session_state['usuario_email'], len(archivos_validos), stats_globales)
                        
                        st.success("¡Todos los archivos procesados con éxito y guardados en tu historial!")
                        
                        st.subheader("📊 Resumen de Limpieza Masiva")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Archivos", len(archivos_validos))
                        col2.metric("Total Duplicados", f"-{total_duplicados}")
                        col3.metric("Total Vacías", f"-{total_vacias}")
                        col4.metric("Total Filtradas", f"-{total_basura}")
                        
                        st.markdown("### 📈 Impacto Visual")
                        total_eliminadas = total_duplicados + total_vacias + total_basura
                        total_limpias = total_originales - total_eliminadas
                        
                        col_chart1, col_chart2 = st.columns(2)
                        
                        with col_chart1:
                            st.caption("Proporción de Datos (Conservados vs Eliminados)")
                            df_resumen = pd.DataFrame({
                                "Estado": ["Conservados", "Eliminados"],
                                "Cantidad": [total_limpias, total_eliminadas]
                            }).set_index("Estado")
                            st.bar_chart(df_resumen, color="#3b82f6")
                            
                        with col_chart2:
                            st.caption("Detalle de Basura Eliminada")
                            df_detalle = pd.DataFrame({
                                "Motivo": ["Duplicados", "Vacías", "Filtro"],
                                "Cantidad": [total_duplicados, total_vacias, total_basura]
                            }).set_index("Motivo")
                            st.bar_chart(df_detalle, color="#ef4444")
                        
                        pdf_bytes = generar_reporte_pdf(
                            st.session_state['usuario_email'], 
                            len(archivos_validos), 
                            stats_globales
                        )
                        
                        st.divider()
                        col_dl1, col_dl2 = st.columns(2)
                        
                        with col_dl1:
                            st.download_button(
                                label="⬇️ Descargar Resultados (.ZIP)",
                                data=zip_buffer.getvalue(),
                                file_name="RowRescue_Limpieza_Masiva.zip",
                                mime="application/zip",
                                type="secondary",
                                use_container_width=True,
                            )
                        
                        with col_dl2:
                            st.download_button(
                                label="📄 Descargar Certificado PDF",
                                data=pdf_bytes,
                                file_name="Reporte_Impacto_RowRescue.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                            )
                        
            except (ValueError, RuntimeError) as e:
                st.warning(f"Aviso sobre tus datos: {e!s}")
            except Exception as e:  # noqa: BLE001
                st.error(f"Error procesando los archivos: {e!s}")