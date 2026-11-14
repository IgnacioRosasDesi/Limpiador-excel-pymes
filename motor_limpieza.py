import logging
from typing import Any

import pandas as pd

# Configuración del Sistema de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("limpieza_tecnico.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def estandarizar_rut(serie_rut: pd.Series) -> pd.Series:
    """Limpia y estandariza una serie de RUTs al formato XXXXXXXX-X de forma vectorizada."""
    rut_limpio = serie_rut.astype(str).str.replace(r"[.\-\s]", "", regex=True).str.upper()
    mask_validos = (rut_limpio.str.len() >= 2) & (~rut_limpio.isin(["NAN", "<NA>", "NONE", "NULL", ""]))

    resultado = rut_limpio.copy()
    resultado.loc[mask_validos] = rut_limpio.loc[mask_validos].str[:-1] + "-" + rut_limpio.loc[mask_validos].str[-1]
    resultado.loc[~mask_validos] = pd.NA
    return resultado


def leer_archivo(archivo):
    """
    Lee el archivo forzando todos los datos a formato texto (str).
    Esto previene colapsos de memoria y corrupción de datos (ej. pérdida de ceros a la izquierda).
    """
    nombre = archivo.name.lower()

    try:
        if nombre.endswith(".csv"):
            df = pd.read_csv(archivo, dtype=str, keep_default_na=False)

        elif nombre.endswith((".xls", ".xlsx")):
            df = pd.read_excel(archivo, dtype=str)
            df.fillna("", inplace=True)

        else:
            raise ValueError("Formato de archivo no soportado. Por favor, sube un .xlsx o .csv")

        return df

    except Exception as e:
        raise RuntimeError(
            f"No se pudo leer el archivo '{archivo.name}'. Asegúrate de que no esté corrupto o protegido con contraseña. (Detalle técnico: {e!s})"
        ) from e


def limpiar_dataframe(
    df: pd.DataFrame, columna_duplicados: str | None = None, valor_basura: str | None = None
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Limpia el DataFrame, elimina duplicados inteligentemente y filtra valores basura."""
    logger.info("Iniciando motor de limpieza de datos...")

    df_cleaned = df.copy()
    filas_orig = len(df_cleaned)
    ruts_detectados = 0
    filas_basura_eliminadas = 0

    try:
        # 1. Filtro avanzado de datos inválidos
        if valor_basura:
            logger.info(f"Buscando y eliminando filas con el valor basura: '{valor_basura}'")
            filas_antes_basura = len(df_cleaned)
            mascara_basura = df_cleaned.astype(str).apply(
                lambda col: col.str.contains(valor_basura, case=False, na=False)
            ).any(axis=1)
            df_cleaned = df_cleaned[~mascara_basura]
            filas_basura_eliminadas = filas_antes_basura - len(df_cleaned)

        # 2. Eliminar filas y columnas 100% vacías
        df_cleaned = df_cleaned.dropna(axis=1, how="all").dropna(how="all")
        filas_vacias = filas_orig - filas_basura_eliminadas - len(df_cleaned)

        # 3. Detección y normalización de RUTs
        for col in df_cleaned.columns:
            if "rut" in str(col).lower() or "run" in str(col).lower():
                df_cleaned[col] = estandarizar_rut(df_cleaned[col])
                ruts_detectados += 1

        # 4. Limpieza de texto vectorizada
        cols_texto = df_cleaned.select_dtypes(include=["object", "string"]).columns
        if not cols_texto.empty:
            for col in cols_texto:
                mask = df_cleaned[col].notna()
                df_cleaned.loc[mask, col] = (
                    df_cleaned.loc[mask, col]
                    .astype(str)
                    .str.replace(r"\s+", " ", regex=True)
                    .str.strip()
                )
            df_cleaned[cols_texto] = df_cleaned[cols_texto].replace(
                regex={r"^(?i)(nan|null|none|)$": pd.NA}
            )

        # 5. Detección y eliminación de duplicados inteligente
        filas_antes_dup = len(df_cleaned)

        if columna_duplicados and columna_duplicados in df_cleaned.columns:
            df_cleaned = df_cleaned.drop_duplicates(subset=[columna_duplicados], keep="last")
        else:
            df_cleaned = df_cleaned.drop_duplicates()

        duplicados = filas_antes_dup - len(df_cleaned)

        # Estadísticas
        stats = {
            "filas_originales": filas_orig,
            "filas_vacias_eliminadas": max(0, filas_vacias),
            "filas_basura_eliminadas": filas_basura_eliminadas,
            "duplicados_eliminados": duplicados,
            "columnas_rut_normalizadas": ruts_detectados,
            "filas_finales": len(df_cleaned),
            "columna_clave_usada": columna_duplicados or "Fila Exacta",
        }

        return df_cleaned, stats

    except Exception as e:
        logger.exception("Fallo crítico en el motor de limpieza.")
        raise RuntimeError(f"Error al limpiar los datos: {e!s}") from e