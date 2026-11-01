# 1. Imports nativos
from io import BytesIO

# 2. Imports de terceros
import pandas as pd
import streamlit as st

from auth_db import iniciar_sesion, registrar_usuario

# 3. Imports locales
from motor_limpieza import leer_archivo, limpiar_dataframe

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

# =========================================================
# PANTALLA DE LOGIN Y REGISTRO (SI NO ESTÁ AUTENTICADO)
# =========================================================
if not st.session_state['usuario_autenticado']:
    st.markdown("<h1 style='text-align: center; color: #3b82f6;'>⚡ RowRescue</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Acceso a la plataforma de DesiLabs</p>", unsafe_allow_html=True)
    st.write("")
    
    # Creamos dos pestañas para separar Login de Registro
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
                        st.rerun() # Recarga la página para entrar
            else:
                st.warning("Por favor ingresa tu correo y contraseña.")
                
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
                with st.spinner("Creando cuenta en los servidores..."):
                    res = registrar_usuario(email_reg, pass_reg)
                    if "error" in res:
                        st.error("Error al registrar: Este correo ya está en uso o es inválido.")
                    else:
                        st.success("✅ ¡Cuenta creada exitosamente! Ahora ve a la pestaña 'Iniciar Sesión' para entrar.")
            else:
                st.warning("Completa todos los campos.")

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

    # --- LÓGICA PRINCIPAL DE LIMPIEZA ---
    archivo_subido = st.file_uploader(
        "Arrastra tu archivo aquí (.xlsx, .csv)", 
        type=["xlsx", "xls", "csv"],
        help="💡 Tus datos están seguros. El archivo se procesa temporalmente en la memoria y se elimina apenas descargas el resultado."
    )

    if archivo_subido:
        try:
            df_raw = leer_archivo(archivo_subido)
            
            st.subheader("⚙️ Opciones de Limpieza", help="Configura cómo quieres que el sistema limpie tu archivo antes de procesarlo.")
            
            opciones_dup = ["Fila exacta (Todas las columnas)"] + list(df_raw.columns)
            columna_seleccionada = st.selectbox(
                "Identificar registros duplicados basándose en:",
                opciones_dup,
                help="""**¿Cómo funciona esto?**\n
    - **Fila exacta:** Solo borrará un registro si TODOS sus datos son 100% idénticos a otro.
    - **Columna específica (Ej. Correo o RUT):** Si eliges una columna, el sistema buscará si ese dato se repite. Si Juan Pérez está 3 veces con el mismo correo, conservará solo el último registro y borrará los antiguos."""
            )
            
            st.markdown("### 🔍 Filtro de Datos Específicos")
            valor_buscado = st.text_input(
                "¿Hay alguna palabra o dato que desees borrar de tu base de datos? (Ej: 'Prueba', 'Cancelado')", 
                placeholder="Escribe aquí para buscar...",
                help="💡 Si tienes filas llenas de datos de prueba o clientes cancelados, escribe la palabra clave aquí. El sistema rastreará todo el documento y te permitirá eliminar esas filas de un solo golpe."
            )
            
            confirmar_basura = False
            
            if valor_buscado:
                mascara = df_raw.astype(str).apply(lambda col: col.str.contains(valor_buscado, case=False, na=False)).any(axis=1)
                coincidencias = mascara.sum()
                
                if coincidencias > 0:
                    st.warning(f"⚠️ **Atención:** Se encontraron **{coincidencias} filas** que contienen la palabra '{valor_buscado}'.")
                    with st.expander("Ver filas que contienen este dato"):
                        st.dataframe(df_raw[mascara].head(5), use_container_width=True)
                    
                    confirmar_basura = st.checkbox(
                        f"🚨 Confirmo que deseo ELIMINAR estas {coincidencias} filas durante la limpieza.",
                        help="Debes marcar esta casilla para autorizar la eliminación de estos registros."
                    )
                else:
                    st.success(f"✅ ¡Todo limpio! La palabra '{valor_buscado}' no existe en esta base de datos.")
            
            st.divider()

            if st.button("✨ Aplicar Limpieza", type="primary", use_container_width=True, help="Haz clic para procesar tu archivo con todas las configuraciones seleccionadas arriba."):
                with st.spinner("Limpiando y normalizando datos..."):
                    
                    clave = None if columna_seleccionada == "Fila exacta (Todas las columnas)" else columna_seleccionada
                    texto_a_borrar = valor_buscado if confirmar_basura else None
                    
                    df_limpio, stats = limpiar_dataframe(df_raw, columna_duplicados=clave, valor_basura=texto_a_borrar)
                    
                    st.success("¡Archivo procesado con éxito!")
                    
                    st.subheader("📊 Resumen de Operación", help="Este es el reporte final de todo lo que el motor limpió por ti.")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Filas Originales", stats["filas_originales"])
                    col2.metric("Duplicados", f"-{stats['duplicados_eliminados']}")
                    col3.metric("Filas Vacías", f"-{stats['filas_vacias_eliminadas']}")
                    col4.metric("Filas Filtradas", f"-{stats['filas_basura_eliminadas']}")
                    
                    if stats.get("columnas_rut_normalizadas", 0) > 0:
                        st.info(f"🇨🇱 Se normalizaron **{stats['columnas_rut_normalizadas']} columna(s) de RUT** al formato oficial.")
                    
                    with st.expander("Ver vista previa de los datos procesados"):
                        st.dataframe(df_limpio.head(15), use_container_width=True)
                        
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df_limpio.to_excel(writer, index=False, sheet_name='RowRescue')
                    
                    st.download_button(
                        label="⬇️ Descargar Base de Datos Limpia (Excel)",
                        data=buffer.getvalue(),
                        file_name="RowRescue_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="secondary",
                        use_container_width=True,
                        help="Descarga tu archivo limpio en formato Excel, listo para usarse."
                    )
                    
        except (ValueError, RuntimeError) as e:
            st.warning(f"Aviso sobre tus datos: {e!s}")
        except Exception as e: # noqa: BLE001
            st.error(f"Error procesando el archivo: {e!s}")