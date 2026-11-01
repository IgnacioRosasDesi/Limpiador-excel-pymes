import firebase_admin
import requests
import streamlit as st
from firebase_admin import credentials, firestore

# 1. Inicialización robusta de Firebase Admin SDK (Firestore)
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            # Convertir secretos a diccionario mutable
            cred_dict = dict(st.secrets["firebase"])
            
            # Normalizar los saltos de línea de la llave privada para evitar errores criptográficos
            if "private_key" in cred_dict:
                pk = cred_dict["private_key"]
                cred_dict["private_key"] = pk.replace("\\n", "\n")
                
            cred = credentials.Certificate(cred_dict)
        else:
            cred = credentials.Certificate("firebase_key.json")
    except Exception:  # noqa: BLE001
        # Fallback seguro para entorno local si faltan secretos en la nube
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