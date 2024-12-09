
import requests
from urllib.parse import urlencode

def enviar_mensaje_whatsapp(numero, api_key, mensaje):
    """Envía un mensaje de WhatsApp utilizando CallMeBot"""
    mensaje_codificado = urlencode({'text': mensaje})
    url = f'https://api.callmebot.com/whatsapp.php?phone={numero}&{mensaje_codificado}&apikey={api_key}'
    response = requests.get(url)
    return response.status_code == 200
