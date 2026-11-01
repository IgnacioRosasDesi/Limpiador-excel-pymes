import firebase_admin
import requests
import streamlit as st
from firebase_admin import credentials, firestore

# 1. Configuración de Firebase Admin usando Secrets de Streamlit o archivo local
if not firebase_admin._apps:
    try:
        # Intentamos leer desde los Secrets configurados en Streamlit Cloud
        secret_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(secret_dict)
    except Exception:  # noqa: BLE001
        # Si estamos en local y no hay secrets configurados, usamos el archivo físico
        cred = credentials.Certificate("firebase_key.json")
    
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Configuración de Firebase REST API (Login/Registro)
try:
    FIREBASE_WEB_API_KEY = st.secrets["FIREBASE_WEB_API_KEY"]
except Exception:  # noqa: BLE001
    FIREBASE_WEB_API_KEY = "TU_API_KEY_AQUI"

def registrar_usuario(email, password):
    """Crea una cuenta nueva en Firebase Auth."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload)
    return r.json()

def iniciar_sesion(email, password):
    """Inicia sesión y devuelve el token y el UID del usuario."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload)
    return r.json()