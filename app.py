# 1. Imports nativos
from io import BytesIO

# 2. Imports de terceros
import pandas as pd
import streamlit as st

# 3. Imports locales
from motor_limpieza import leer_archivo, limpiar_dataframe

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="DataClean Pro | PyMEs", 
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

# --- CABECERA DE LA APP ---
col_logo, col_texto = st.columns([1, 6])
with col_logo:
    st.markdown("<h1 style='text-align: center; color: #3b82f6;'>⚡</h1>", unsafe_allow_html=True)
with col_texto:
    st.markdown("<h1 style='margin-bottom: 0px;'>DataClean Pro</h1>", unsafe_allow_html=True)

st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>Plataforma inteligente de estandarización y limpieza de bases de datos.</p>", unsafe_allow_html=True)
st.divider()

# --- LÓGICA PRINCIPAL ---
archivo_subido = st.file_uploader("Arrastra tu archivo aquí (.xlsx, .csv)", type=["xlsx", "xls", "csv"])

if archivo_subido:
    try:
        df_raw = leer_archivo(archivo_subido)
        
        st.subheader("⚙️ Opciones de Limpieza")
        
        # 1. Opciones de duplicados
        opciones_dup = ["Fila exacta (Todas las columnas)"] + list(df_raw.columns)
        columna_seleccionada = st.selectbox(
            "Identificar registros duplicados basándose en:",
            opciones_dup,
            help="Si eliges una columna (ej. Correo), se eliminarán los repetidos conservando solo el registro más reciente."
        )
        
        # 2. NUEVO: Filtro Interactivo de Datos Inválidos
        st.markdown("### 🔍 Filtro de Datos Específicos")
        valor_buscado = st.text_input(
            "¿Hay alguna palabra o dato que desees borrar de tu base de datos? (Ej: 'Prueba', 'Cancelado')", 
            placeholder="Escribe aquí para buscar..."
        )
        
        confirmar_basura = False # Variable de control
        
        if valor_buscado:
            # Buscamos instantáneamente en el dataframe crudo
            mascara = df_raw.astype(str).apply(lambda col: col.str.contains(valor_buscado, case=False, na=False)).any(axis=1)
            coincidencias = mascara.sum()
            
            if coincidencias > 0:
                st.warning(f"⚠️ **Atención:** Se encontraron **{coincidencias} filas** que contienen la palabra '{valor_buscado}'.")
                with st.expander("Ver filas que contienen este dato"):
                    st.dataframe(df_raw[mascara].head(5), use_container_width=True)
                
                # Casilla de confirmación requerida por el usuario
                confirmar_basura = st.checkbox(f"🚨 Confirmo que deseo ELIMINAR estas {coincidencias} filas durante la limpieza.")
            else:
                st.success(f"✅ ¡Todo limpio! La palabra '{valor_buscado}' no existe en esta base de datos.")
        
        st.divider()

        # 3. Lógica del botón de limpieza
        if st.button("✨ Aplicar Limpieza", type="primary", use_container_width=True):
            with st.spinner("Limpiando y normalizando datos..."):
                
                clave = None if columna_seleccionada == "Fila exacta (Todas las columnas)" else columna_seleccionada
                
                # Solo pasamos el valor a borrar si el usuario marcó la casilla de confirmación
                texto_a_borrar = valor_buscado if confirmar_basura else None
                
                df_limpio, stats = limpiar_dataframe(df_raw, columna_duplicados=clave, valor_basura=texto_a_borrar)
                
                st.success("¡Archivo procesado con éxito!")
                
                # Resultados visuales actualizados
                st.subheader("📊 Resumen de Operación")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Filas Originales", stats["filas_originales"])
                col2.metric("Duplicados", f"-{stats['duplicados_eliminados']}")
                col3.metric("Filas Vacías", f"-{stats['filas_vacias_eliminadas']}")
                col4.metric("Filas Filtradas", f"-{stats['filas_basura_eliminadas']}")
                
                if stats.get("columnas_rut_normalizadas", 0) > 0:
                    st.info(f"🇨🇱 Se normalizaron **{stats['columnas_rut_normalizadas']} columna(s) de RUT** al formato oficial.")
                
                with st.expander("Ver vista previa de los datos procesados"):
                    st.dataframe(df_limpio.head(15), use_container_width=True)
                    
                # Descarga
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_limpio.to_excel(writer, index=False, sheet_name='DataClean_Pro')
                
                st.download_button(
                    label="⬇️ Descargar Base de Datos Limpia (Excel)",
                    data=buffer.getvalue(),
                    file_name="DataClean_Pro_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="secondary",
                    use_container_width=True
                )
                
    except (ValueError, RuntimeError) as e:
        st.warning(f"Aviso sobre tus datos: {e!s}")
    except Exception as e:  # noqa: BLE001
        st.error(f"Error procesando el archivo: {e!s}")