import json
import re
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import streamlit as st


def _normalizar_llave_privada(pk: str) -> str:
    """Extrae y reconstruye la estructura PEM estándar a partir de cualquier base64 corrompido."""
    if not isinstance(pk, str):
        return pk
    
    # 1. Limpiar encabezados, pies y caracteres de escape
    limpio = (
        pk.replace("-----BEGIN PRIVATE KEY-----", "")
        .replace("-----END PRIVATE KEY-----", "")
        .replace("\\n", "\n")
        .replace("\r", "")
    )
    
    # 2. Aislar únicamente los caracteres válidos de Base64 (A-Z, a-z, 0-9, +, /, =)
    base64_solo = "".join(re.findall(r'[A-Za-z0-9+/=]', limpio))
    
    # 3. Fragmentar exactamente en bloques de 64 caracteres (estándar PEM oficial)
    lineas_chunk = [base64_solo[i:i + 64] for i in range(0, len(base64_solo), 64)]
    base64_formateado = "\n".join(lineas_chunk)
    
    return f"-----BEGIN PRIVATE KEY-----\n{base64_formateado}\n-----END PRIVATE KEY-----\n"


# 1. Inicialización robusta leyendo el string JSON desde los Secrets
if not firebase_admin._apps:
    if "FIREBASE_JSON_STR" in st.secrets:
        try:
            raw_json = st.secrets["FIREBASE_JSON_STR"]
            cred_dict = json.loads(raw_json)
            
            if "private_key" in cred_dict:
                cred_dict["private_key"] = _normalizar_llave_privada(cred_dict["private_key"])
                
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:  # noqa: BLE001
            st.error(f"Error crítico al inicializar las credenciales de Firebase: {e}")
            st.stop()
    else:
        st.error("⚠️ Falta configurar el secreto 'FIREBASE_JSON_STR' en el panel de Streamlit Cloud.")
        st.stop()

db = firestore.client()

# 2. Configuración de Firebase REST API (Auth)
try:
    FIREBASE_WEB_API_KEY = st.secrets["FIREBASE_WEB_API_KEY"]
except Exception:  # noqa: BLE001
    FIREBASE_WEB_API_KEY = "AIzaSyDMWU7kE5BXN8qrhUZD2mZgwkbNN4l6DFw"


def registrar_usuario(email: str, password: str) -> dict:
    """Crea una cuenta de usuario nueva en Firebase Authentication."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload, timeout=10)
    return response.json()


def iniciar_sesion(email: str, password: str) -> dict:
    """Inicia sesión y recupera el token de acceso y UID del usuario."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload, timeout=10)
    return response.json()