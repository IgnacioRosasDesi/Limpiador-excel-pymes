import os

import mercadopago


def generar_link_mercadopago(email_usuario: str, url_retorno: str = "http://localhost:5173") -> str:
    """
    Se conecta a la API de Mercado Pago y genera un link de checkout seguro.
    """
    ACCESS_TOKEN = os.environ.get(
        "MP_ACCESS_TOKEN",
        "APP_USR-4556958156312089-110922-27e1b2963289238e0e564bb41ca855c3-3832446080",
    )

    sdk = mercadopago.SDK(ACCESS_TOKEN)

    preference_data = {
        "items": [
            {
                "title": "RowRescue Premium - Acceso Ilimitado",
                "description": "Licencia profesional para limpieza masiva de datos",
                "quantity": 1,
                "currency_id": "CLP",
                "unit_price": 5000,
            }
        ],
        "payer": {"email": email_usuario},
        "back_urls": {
            "success": f"{url_retorno}?pago=exitoso&user={email_usuario}",
            "failure": f"{url_retorno}?pago=fallido",
            "pending": f"{url_retorno}?pago=pendiente",
        },
        "auto_return": "approved",
        "external_reference": email_usuario,
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        return preference_response["response"]["init_point"]
    except Exception as e: # noqa: BLE001
        print(f"Error generando link de pago: {e}")
        return ""