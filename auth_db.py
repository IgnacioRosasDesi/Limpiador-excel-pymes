import firebase_admin
import requests
import streamlit as st
from firebase_admin import credentials, firestore

# 1. Configuración de Firebase Admin con tus credenciales integradas
if not firebase_admin._apps:
    try:
        cred_dict = {
            "type": "service_account",
            "project_id": "rowrescue",
            "private_key_id": "98619e127b398bf41785a72fb7b09313c486d00a",
            "private_key": (
                "-----BEGIN PRIVATE KEY-----\n"
                "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDZxh5FjzLx9fNu\n"
                "abyPu8mCQ5NmMB0bDwD0+qvWVBCwV++tDQPnHWVuIjNjVvVR2/1vnCwKJrxr2zCY\n"
                "FnVz1mPfJNfsALeWuIB1gQwkIUAx7VTh4lvriHzam6pZrMKocmY5THvfpERCgAbf\n"
                "seKNnTIakFD518JmWQD2bAmBV7E/z6AV5EFr5GfuJnIOZN0Z+wbFVZ2zNPYWI9zi\n"
                "ZSSgb91CMfeY0INBxtOD1RWmUL+flYUt4uaiEfWHp8nDatpNj4QxcX2CQtEuzNCf\n"
                "JJQjbxPpffrWs4UD5Y9M9ViGVApBJYx4CEWgxHsDOFJDluewvl6CgTtShL3WFhru\n"
                "FMofvF5pAgMBAAECggEAQNyUxJP/kPh3zjF5A3hjbsRwwPVgneAMoWqNxrLYG6W9\n"
                "UZX4TRxAyxotow9R1tVGeTkTFtztrtQkd4/s4JkAuwQOuZCHHcGLJTRP6OzsYVJ2\n"
                "Pyb7yL2orjXB+Z6Ohbw4/STuGjCjUgkuwu6I8zPYKfhE3f0ovfIRatPHyvnS5ZWF\n"
                "QoLl8+sYBciqUGlVSJn17AB7mfcnIROUuaZpcW4Eljdm45q03YSRFZRA2A3US0SK\n"
                "uXvfX4IdzCkltlaihbv+/A8QYxaYknZ0dgDqmLJMoJhkXkrI0fqyHb7yh9UJMyJI\n"
                "/7zeETlJovvh3ELK1YpL9U6XEWgYdPWmjrK/mrY63wKBgQDxLof6WJ+Az7++JroY\n"
                "DyvRLKlAz7paBdbdrxUVYhpQ8M17vKtPliaWNkx03md5P1iryG3+0bb2Mg/+wMWI\n"
                "1e/qnTYAD2YbxfqyUgUCKlpJ1g2iGUNqmpIXzdA1ldmdzksvVg97dP5q7Ye2yrKi\n"
                "d1VXru+U0hdPmddF5Ok1eIESYwKBgQDnJ2mYsw5ls13Q5RTa5+uJo2wfsA0krjku\n"
                "vc4Gwq++M6JoXXpmZmiejFVw96YO4SA6+yl7oo747+FMT04ElXZ1EJ2HzUv/tSw\n"
                "nsyVSiPwiY2YATijUq0TCtpMU7FogV1yh5iKZ3tmhCNrOfuvp8j/EUgHzXTw11sv\n"
                "0Fuz2Rc/wwKBgBT+sPWZC2GCNDXQVzjK8UyHL8CllJpLkdXAbPxsis/q9mhEF0GZ\n"
                "V4iR93vg9G74lbZ2fyTEisHJv9y0WT29KeJphw7gSEo4pMcrHqZ+m1d8G7m1q0m3\n"
                "ZOpPj0Vq4wO6to7LVhOwLomOXdcKtBwyeSpl3xM8aq0SPkwmTirKb6nzAoGAGafs\n"
                "NoCZNnyECy2B9RIMuIgk9hdqPgoAWsm1JosJ1Ex1UB1VownjXX9Gfohw6mCgwlZt\n"
                "O7WQLjmHBleCvfh7AuRmRAoOszcLkFbvyhoihw4dYyOvj6EbiKOJuzMG29yP7KhU\n"
                "K/h0X9qGu94Bq2tqCbV3UzZgpmKgwlvT8dBEnlUCgYEAnPScbLi3cFruUMkj4p4r\n"
                "uaUm52hmgwTN+y+yfE07apdZvMkkZ1OwBg9eAccPL8eFuTjS0a36tJVMqKFYzOff\n"
                "nVnTrP0gS1857O1i+dhmireHDgjG8bMxpy4Bu+c1RoPZ8B6ClyGm8K5WoIGZN9/RD\n"
                "dCHtR/M7B1Wtv94eiqFfnlI=\n"
                "-----END PRIVATE KEY-----"
            ),
            "client_email": "firebase-adminsdk-fbsvc@rowrescue.iam.gserviceaccount.com",
            "client_id": "108829409024285353247",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40rowrescue.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        cred = credentials.Certificate(cred_dict)
    except Exception:  # noqa: BLE001
        cred = credentials.Certificate("firebase_key.json")
    
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Configuración de Firebase REST API (Login/Registro)
try:
    FIREBASE_WEB_API_KEY = st.secrets["FIREBASE_WEB_API_KEY"]
except Exception:  # noqa: BLE001
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