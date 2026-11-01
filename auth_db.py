import firebase_admin
import requests
import streamlit as st
from firebase_admin import credentials, firestore

# 1. Inicialización basada en la documentación oficial de Streamlit para Secrets
if not firebase_admin._apps:
    try:
        # Verificamos si los secretos de Firebase existen en el entorno de Streamlit
        if "firebase" in st.secrets:
            # Convertimos el objeto de secretos a un diccionario mutable estándar
            cred_dict = dict(st.secrets["firebase"])
            
            # Normalización estricta del formato PEM de la llave privada
            if "private_key" in cred_dict:
                private_key_raw = cred_dict["private_key"]
                # Aseguramos que los saltos de línea sean interpretados de manera real
                cred_dict["private_key"] = private_key_raw.replace("\\n", "\n")
            
            cred = credentials.Certificate(cred_dict)
        else:
            # Fallback local si no se detectan secretos en la nube
            cred = credentials.Certificate("firebase_key.json")
    except Exception:  # noqa: BLE001
        # Captura blindada para entorno local con archivo físico
        cred = credentials.Certificate("firebase_key.json")
    
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Configuración de Firebase REST API (Auth) con respaldo seguro
try:
    FIREBASE_WEB_API_KEY = st.secrets["FIREBASE_WEB_API_KEY"]
except Exception:  # noqa: BLE001
    FIREBASE_WEB_API_KEY = "AizaSyDMWU7ke5BXN8qrhUZD2mZgwkbNN4l6DFw"


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