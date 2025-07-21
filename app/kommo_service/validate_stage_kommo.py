import os
import aiofiles
import aiohttp
import base64
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

# 2) Enviar imagen a OpenAI GPT-4o con visión
def validate_stage_kommo(lead_id):
    token = os.getenv("TOKEN_KOMMO")
    subdomain = os.getenv("SUBDOMAIN_KOMMO")
    if not token:
        raise ValueError("TOKEN_KOMMO no está definida")

    try:
        url = f"https://{subdomain}.kommo.com/v4/leads/{lead_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        print(f"Datos del lead: {data}")
        if response.status_code != 200:
            raise Exception(f"Error al obtener el lead: {data.get('error', 'Unknown error')}")
        
        # Validación de IDs
        status_id = data.get("status_id")
        pipeline_id = data.get("pipeline_id")
        if status_id == 58141807 and pipeline_id == 6950551:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error validando etapa del lead en Kommo: {e}")
        raise