import firebase_admin
import requests
import streamlit as st
from firebase_admin import credentials, firestore

# 1. Inicialización simple y directa
if not firebase_admin._apps:
    if "firebase" in st.secrets:
        cred_dict = dict(st.secrets["firebase"])
        
        # EL TRUCO DEFINITIVO: Limpiar caracteres fantasma de Windows (\r) 
        # y asegurar que los saltos de línea (\n) sean puros.
        pk = cred_dict["private_key"]
        pk = pk.replace("\\n", "\n").replace("\r", "")
        cred_dict["private_key"] = pk
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Respaldo local
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Configuración de Firebase REST API (Auth)
FIREBASE_WEB_API_KEY = st.secrets.get("FIREBASE_WEB_API_KEY", "TU_API_KEY_LOCAL")

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