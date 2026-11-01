# ⚡ RowRescue | Data Standardization Micro-SaaS

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_Framework-FF4B4B.svg)
![Status](https://img.shields.io/badge/Status-Live_in_Production-success.svg)

**🌐 Live Demo:** [RowRescue App](https://rowrescue.streamlit.app)

RowRescue es una plataforma web (Micro-SaaS) diseñada para resolver uno de los mayores cuellos de botella de las PyMEs: la limpieza y estandarización de bases de datos. Construido con Python y Pandas, procesa miles de filas en milisegundos mediante operaciones vectorizadas.

## 🚀 Características Principales

- **Normalización Automática de RUT (Chile):** Detecta columnas de identificación y estandariza formatos caóticos (ej. `19.123.456-k` ➔ `19123456-K`).
- **Eliminación Inteligente de Duplicados:** Permite seleccionar columnas clave (como "Correo" o "RUT") para conservar siempre el registro más reciente.
- **Filtro Avanzado de Datos Inválidos:** Buscador interactivo que rastrea y elimina registros basura con confirmación previa del usuario.
- **Optimización de Rendimiento:** Uso de métodos nativos vectorizados de Pandas, reduciendo drásticamente la complejidad temporal frente a iteraciones tradicionales.
- **Seguridad y Privacidad:** Arquitectura efímera donde los datos se procesan en memoria y se descartan inmediatamente tras la exportación.

## 🛠️ Stack Tecnológico
- **Backend / Data Pipeline:** Python, Pandas.
- **Frontend / UI:** Streamlit (Custom CSS & Corporate Branding).
- **Despliegue:** Streamlit Community Cloud.

## 💡 Sobre el Desarrollador
Desarrollado por **Ignacio Rosas**, Ingeniero en Informática especializado en automatización de procesos, procesamiento de datos y desarrollo de soluciones de software para negocios.