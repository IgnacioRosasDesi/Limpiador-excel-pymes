# 1. Imports nativos de Python
from io import BytesIO

# 2. Imports de librerías de terceros
import pandas as pd
import streamlit as st

# 3. Imports locales de nuestra aplicación
from motor_limpieza import procesar_archivo

# Configuración de la página web
st.set_page_config(
    page_title="Limpiador de Datos PyME", 
    page_icon="🧹", 
    layout="centered"
)

st.title("🧹 Limpiador Inteligente de Datos")
st.markdown("Sube tus archivos de Excel o CSV desordenados y obtén una base de datos limpia, sin duplicados ni espacios en blanco. Ideal para limpiar contactos, inventarios o reportes.")

# Zona para arrastrar y soltar el archivo
archivo_subido = st.file_uploader("Arrastra tu archivo aquí (.xlsx, .csv)", type=["xlsx", "xls", "csv"])

if archivo_subido:
    with st.spinner("Procesando y limpiando datos..."):
        try:
            # Llamamos a nuestro motor de limpieza
            df_limpio, stats = procesar_archivo(archivo_subido)
            
            st.success("¡Archivo limpiado con éxito!")
            
            # Mostramos los resultados visuales al usuario
            st.subheader("📊 Resumen de la Limpieza")
            col1, col2, col3 = st.columns(3)
            col1.metric("Filas Originales", stats["filas_originales"])
            col2.metric("Duplicados Eliminados", f"-{stats['duplicados_eliminados']}")
            col3.metric("Filas Vacías Eliminadas", f"-{stats['filas_vacias_eliminadas']}")
            
            st.markdown(f"**Resultado:** Tu archivo pasó de {stats['filas_originales']} a **{stats['filas_finales']} filas útiles**.")
            
            # Vista previa colapsable
            with st.expander("Ver vista previa de los datos limpios"):
                st.dataframe(df_limpio.head(15), use_container_width=True)
                
            # Preparar el archivo limpio para su descarga en Excel
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_limpio.to_excel(writer, index=False, sheet_name='Datos_Limpios')
            
            st.download_button(
                label="⬇️ Descargar Archivo Limpio (Excel)",
                data=buffer.getvalue(),
                file_name="datos_limpios.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
            
        except (ValueError, RuntimeError) as e:
            # Capturamos los errores específicos de formato o estructura que definimos en el motor
            st.warning(f"Aviso sobre tus datos: {e!s}")
        except Exception as e:  # noqa: BLE001
            # Bloque de seguridad final por si ocurre un fallo no documentado (silenciando la advertencia del linter)
            st.error(f"Error inesperado del sistema: {e!s}")