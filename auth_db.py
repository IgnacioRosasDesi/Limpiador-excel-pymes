import firebase_admin
from firebase_admin import credentials, firestore
import requests
import streamlit as st

# Inicialización simple y directa basada en la estructura oficial de Streamlit
if not firebase_admin._apps:
    if "firebase" in st.secrets:
        # Convertimos el secreto de Firebase en un diccionario estándar
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Respaldo local por si pruebas en tu PC
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)

db = firestore.client()

# Web API Key para Autenticación (Login / Registro)
FIREBASE_WEB_API_KEY = st.secrets.get("FIREBASE_WEB_API_KEY", "AIzaSyDMWU7kE5BXN8qrhUZD2mZgwkbNN4l6DFw")


def registrar_usuario(email: str, password: str) -> dict:
    """Crea una cuenta nueva en Firebase Auth."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload, timeout=10)
    return response.json()


def iniciar_sesion(email: str, password: str) -> dict:
    """Inicia sesión y devuelve los datos del usuario."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload, timeout=10)
    return response.json()