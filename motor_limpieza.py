import logging
from typing import Any

import pandas as pd

# Configuración del Sistema de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("limpieza_tecnico.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def limpiar_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Limpia el DataFrame de forma vectorizada y retorna estadísticas."""
    logger.info("Iniciando motor de limpieza de datos...")
    
    filas_orig, cols_orig = df.shape

    try:
        # 1. Eliminar filas y columnas 100% vacías simultáneamente
        df_cleaned = df.dropna(axis=1, how='all').dropna(how='all')
        
        filas_vacias = filas_orig - df_cleaned.shape[0]
        cols_vacias = cols_orig - df_cleaned.shape[1]
        logger.info(f"Vaciado: {filas_vacias} filas y {cols_vacias} columnas eliminadas.")

        # 2. Limpieza de texto vectorizada (Máximo rendimiento en Pandas)
        cols_texto = df_cleaned.select_dtypes(include=['object', 'string']).columns
        if not cols_texto.empty:
            for col in cols_texto:
                mask = df_cleaned[col].notna()
                # Reduce espacios múltiples a uno solo y limpia los bordes nativamente
                df_cleaned.loc[mask, col] = (
                    df_cleaned.loc[mask, col]
                    .astype(str)
                    .str.replace(r'\s+', ' ', regex=True)
                    .str.strip()
                )
            # Reemplaza nulos textuales por valores nulos reales de Pandas (<NA>)
            df_cleaned[cols_texto] = df_cleaned[cols_texto].replace(
                regex={r'^(?i)(nan|null|none|)$': pd.NA}
            )

        # 3. Detección y eliminación de duplicados
        filas_antes_dup = len(df_cleaned)
        df_cleaned = df_cleaned.drop_duplicates()
        duplicados = filas_antes_dup - len(df_cleaned)
        logger.info(f"Duplicados eliminados: {duplicados} filas.")

        # 4. Consolidar estadísticas
        stats = {
            "filas_originales": filas_orig,
            "columnas_originales": cols_orig,
            "filas_vacias_eliminadas": filas_vacias,
            "columnas_vacias_eliminadas": cols_vacias,
            "duplicados_eliminados": duplicados,
            "filas_finales": len(df_cleaned),
            "columnas_finales": len(df_cleaned.columns)
        }

        logger.info("Limpieza finalizada con éxito.")
        return df_cleaned, stats

    except Exception as e:
        logger.exception("Fallo crítico en el motor de limpieza.")
        raise RuntimeError(f"Error al limpiar los datos: {e!s}") from e


def procesar_archivo(ruta_o_buffer) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Lee el archivo manejando fallos comunes de encoding y ejecuta la limpieza."""
    nombre_archivo = getattr(ruta_o_buffer, 'name', str(ruta_o_buffer))
    logger.info(f"=== Nueva solicitud: {nombre_archivo} ===")

    try:
        if nombre_archivo.lower().endswith('.csv'):
            try:
                df = pd.read_csv(ruta_o_buffer, encoding='utf-8')
            except UnicodeDecodeError:
                logger.warning("Fallo UTF-8 en CSV. Aplicando fallback a Latin-1...")
                if hasattr(ruta_o_buffer, 'seek'):
                    ruta_o_buffer.seek(0)
                df = pd.read_csv(ruta_o_buffer, encoding='latin1', sep=None, engine='python')
                
        elif nombre_archivo.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(ruta_o_buffer)
        else:
            raise ValueError("Formato no soportado. Sube archivos Excel (.xlsx, .xls) o CSV.")

        if df.empty:
            raise ValueError("El archivo está completamente vacío.")

        return limpiar_dataframe(df)

    except pd.errors.EmptyDataError:
        logger.error("EmptyDataError de pandas detectado. Archivo corrupto.")
        raise ValueError("El archivo parece estar corrupto o no tiene estructura de tabla.")
    except Exception:
        logger.exception("Error inesperado al leer el archivo.")
        raise