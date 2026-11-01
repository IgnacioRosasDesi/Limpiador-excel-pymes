import firebase_admin
import requests
from firebase_admin import credentials, firestore

# 1. Configuración de Firebase Admin (Para interactuar con Firestore)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Configuración de Firebase REST API (Para el Login/Registro)
# REEMPLAZA ESTO CON TU WEB API KEY DE FIREBASE
FIREBASE_WEB_API_KEY = "AIzaSyDMWU7kE5BXN8qrhUZD2mZgwkbNN4l6DFw"

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