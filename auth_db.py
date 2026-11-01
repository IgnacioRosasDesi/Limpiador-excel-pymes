import firebase_admin
import requests
import streamlit as st
from firebase_admin import credentials, firestore

# 1. Configuración de Firebase Admin segura para Producción y Local
if not firebase_admin._apps:
    try:
        # Intentar cargar desde los secretos de Streamlit Cloud
        if "firebase" in st.secrets:
            cred_dict = dict(st.secrets["firebase"])
            
            # Normalizar los saltos de línea de la llave privada
            pk = cred_dict.get("private_key", "")
            if "\\n" in pk:
                pk = pk.replace("\\n", "\n")
            cred_dict["private_key"] = pk
            
            cred = credentials.Certificate(cred_dict)
        else:
            raise Exception("Secrets no encontrados")
    except Exception:  # noqa: BLE001
        # Fallback para entorno local con archivo físico
        cred = credentials.Certificate("firebase_key.json")
    
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Configuración de Firebase REST API (Login/Registro)
try:
    FIREBASE_WEB_API_KEY = st.secrets["FIREBASE_WEB_API_KEY"]
except Exception:  # noqa: BLE001
    FIREBASE_WEB_API_KEY = "AizaSyDMWU7ke5BXN8qrhUZD2mZgwkbNN4l6DFw"

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