from datetime import UTC, datetime

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

def guardar_historial_limpieza(email: str, num_archivos: int, stats: dict):
    """Guarda un registro automático de la limpieza en Firestore."""
    try:
        doc_ref = db.collection("historial_limpiezas").document()
        doc_ref.set({
            "email": email,
            "fecha": datetime.now(UTC).isoformat(),
            "num_archivos": num_archivos,
            "filas_originales": stats.get("originales", 0),
            "duplicados_eliminados": stats.get("duplicados", 0),
            "vacias_eliminadas": stats.get("vacias", 0),
            "basura_eliminada": stats.get("basura", 0)
        })
    except Exception as e: # noqa: BLE001
        print(f"Error guardando historial en Firestore: {e}")

def obtener_historial_usuario(email: str) -> list:
    """Recupera el historial de limpiezas recientes del usuario desde Firestore."""
    try:
        docs = db.collection("historial_limpiezas")\
                 .where("email", "==", email)\
                 .stream()
        
        historial = [doc.to_dict() for doc in docs]
        # Ordenar de más reciente a más antiguo en memoria (evita requerir índices compuestos en Firebase)
        historial.sort(key=lambda x: x.get("fecha", ""), reverse=True)
        return historial[:10] # Retorna los últimos 10 registros
    except Exception as e: # noqa: BLE001
        print(f"Error obteniendo historial: {e}")
        return []

def guardar_preset_usuario(email: str, nombre_preset: str, columna: str, texto_basura: str):
    """Guarda una configuración de limpieza favorita en Firestore."""
    try:
        doc_ref = db.collection("presets_limpieza").document()
        doc_ref.set({
            "email": email,
            "nombre_preset": nombre_preset,
            "columna": columna,
            "texto_basura": texto_basura,
            "fecha": datetime.now(UTC).isoformat()
        })
        return True
    except Exception as e:  # noqa: BLE001
        print(f"Error guardando preset: {e}")
        return False

def obtener_presets_usuario(email: str) -> list:
    """Recupera los presets guardados del usuario desde Firestore."""
    try:
        docs = db.collection("presets_limpieza")\
                 .where("email", "==", email)\
                 .stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:  # noqa: BLE001
        print(f"Error obteniendo presets: {e}")
        return []

def eliminar_preset_usuario(email: str, nombre_preset: str):
    """Elimina un preset guardado del usuario."""
    try:
        docs = db.collection("presets_limpieza")\
                 .where("email", "==", email)\
                 .where("nombre_preset", "==", nombre_preset)\
                 .stream()
        for doc in docs:
            doc.reference.delete()
        return True
    except Exception as e:  # noqa: BLE001
        print(f"Error eliminando preset: {e}")
        return False

def obtener_perfil_usuario(email: str) -> dict:
    """Obtiene el plan actual del usuario. Si es nuevo, lo crea como 'free'."""
    try:
        doc_ref = db.collection("usuarios_perfiles").document(email)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            # Si no existe en la BD, lo inicializamos como free
            perfil_base = {"email": email, "plan": "free", "fecha_registro": datetime.now(UTC).isoformat()}
            doc_ref.set(perfil_base)
            return perfil_base
    except Exception as e: # noqa: BLE001
        print(f"Error obteniendo perfil: {e}")
        return {"email": email, "plan": "free"}

def actualizar_plan_usuario(email: str, nuevo_plan: str):
    """Actualiza el plan del usuario (ej. de 'free' a 'premium')."""
    try:
        db.collection("usuarios_perfiles").document(email).update({"plan": nuevo_plan})
        return True
    except Exception as e: # noqa: BLE001
        print(f"Error actualizando plan: {e}")
        return False