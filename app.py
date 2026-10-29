# 1. Imports nativos
from io import BytesIO

# 2. Imports de terceros
import pandas as pd
import streamlit as st

# 3. Imports locales
from motor_limpieza import leer_archivo, limpiar_dataframe

st.set_page_config(
    page_title="Limpiador de Datos PyME", 
    page_icon="🧹", 
    layout="centered"
)

st.title("🧹 Limpiador Inteligente de Datos")
st.markdown("Sube tus archivos de Excel o CSV desordenados y obtén una base de datos limpia. Selecciona parámetros avanzados para un control total.")

archivo_subido = st.file_uploader("Arrastra tu archivo aquí (.xlsx, .csv)", type=["xlsx", "xls", "csv"])

if archivo_subido:
    try:
        # Leemos el archivo de forma invisible primero
        df_raw = leer_archivo(archivo_subido)
        
        st.divider()
        st.subheader("⚙️ Opciones de Limpieza")
        
        # Armamos las opciones de duplicados con la lista real de columnas
        opciones_dup = ["Fila exacta (Todas las columnas)"] + list(df_raw.columns)
        
        columna_seleccionada = st.selectbox(
            "Identificar registros duplicados basándose en:",
            opciones_dup,
            help="Si eliges una columna (ej. Correo), se eliminarán los repetidos conservando solo el registro más reciente."
        )
        
        # Lógica del botón de limpieza
        if st.button("✨ Aplicar Limpieza", type="primary", use_container_width=True):
            with st.spinner("Limpiando y normalizando datos..."):
                
                # Determinamos si usar una columna específica o todo el dataframe
                clave = None if columna_seleccionada == "Fila exacta (Todas las columnas)" else columna_seleccionada
                
                df_limpio, stats = limpiar_dataframe(df_raw, columna_duplicados=clave)
                
                st.success("¡Archivo limpiado con éxito!")
                
                # Resultados visuales
                st.subheader("📊 Resumen de la Limpieza")
                col1, col2, col3 = st.columns(3)
                col1.metric("Filas Originales", stats["filas_originales"])
                col2.metric(f"Duplicados ({stats['columna_clave_usada']})", f"-{stats['duplicados_eliminados']}")
                col3.metric("Filas Vacías Eliminadas", f"-{stats['filas_vacias_eliminadas']}")
                
                if stats.get("columnas_rut_normalizadas", 0) > 0:
                    st.info(f"🇨🇱 Se normalizaron **{stats['columnas_rut_normalizadas']} columna(s) de RUT** al formato XXXXXXXX-X.")
                
                with st.expander("Ver vista previa de los datos limpios"):
                    st.dataframe(df_limpio.head(15), use_container_width=True)
                    
                # Descarga
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_limpio.to_excel(writer, index=False, sheet_name='Datos_Limpios')
                
                st.download_button(
                    label="⬇️ Descargar Archivo Limpio (Excel)",
                    data=buffer.getvalue(),
                    file_name="datos_limpios.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="secondary",
                    use_container_width=True
                )
                
    except (ValueError, RuntimeError) as e:
        st.warning(f"Aviso sobre tus datos: {e!s}")
    except Exception as e:  # noqa: BLE001
        st.error(f"Error procesando el archivo: {e!s}")