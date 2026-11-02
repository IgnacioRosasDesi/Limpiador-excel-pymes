import firebase_admin
import requests
import streamlit as st
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("firebase_key.json")
    
    firebase_admin.initialize_app(cred)

db = firestore.client()

FIREBASE_WEB_API_KEY = st.secrets.get("FIREBASE_WEB_API_KEY", "AIzaSyDMWU7kE5BXN8qrhUZD2mZgwkbNN4l6DFw")

def registrar_usuario(email: str, password: str) -> dict:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload, timeout=10)
    return response.json()

def iniciar_sesion(email: str, password: str) -> dict:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload, timeout=10)
    return response.json()

def enviar_correo_verificacion(id_token: str) -> dict:
    """Envía un enlace de verificación único al correo recién registrado."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
    payload = {"requestType": "VERIFY_EMAIL", "idToken": id_token}
    response = requests.post(url, json=payload, timeout=10)
    return response.json()

def enviar_recuperacion_clave(email: str) -> dict:
    """Envía un enlace de seguridad para restablecer la contraseña olvidada."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
    payload = {"requestType": "PASSWORD_RESET", "email": email}
    response = requests.post(url, json=payload, timeout=10)
    return response.json()