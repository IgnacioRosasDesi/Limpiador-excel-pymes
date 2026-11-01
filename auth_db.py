import json

import firebase_admin
import requests
import streamlit as st
from firebase_admin import credentials, firestore

# 1. Inicialización de Firebase Admin usando string JSON desde Secrets
if not firebase_admin._apps:
    if "FIREBASE_JSON_STR" in st.secrets:
        try:
            raw_json = st.secrets["FIREBASE_JSON_STR"]
            cred_dict = json.loads(raw_json)

            if "private_key" in cred_dict:
                cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")

            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e: # noqa: BLE001
            st.error(f"Error parseando el JSON de credenciales de Firebase: {e}")
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