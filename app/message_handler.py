import os
import aiofiles
import aiohttp
import base64
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

# 1) Descargar archivos desde URL
async def download_file(url: str, path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            async with aiofiles.open(path, 'wb') as f:
                await f.write(await resp.read())
    return path

# 2) Enviar imagen a OpenAI GPT-4o con visión
def analyze_image_with_gpt4o(image_path: str, prompt: str = "Extrae la información en formato JSON con los campos 'producto' y 'cantidad'."):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY no está definida")

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# 3) Procesar los datos del mensaje recibido
async def process_request_data(form_data: dict):
    msg = form_data["message"]["add"][0]
    lead_id = int(msg["entity_id"])
    text = msg.get("text", "").strip()
    att = msg.get("attachment")

    result_text = text

    if att and att["type"] == "picture":
        url = att["link"]
        filename = att["file_name"]
        temp_path = f"/tmp/{filename}"

        # Descargar imagen y procesarla con GPT-4o
        await download_file(url, temp_path)
        try:
            vision_summary = analyze_image_with_gpt4o(temp_path)
            result_text += f"\n[Resumen IA de imagen:]\n{vision_summary}"
        except Exception as e:
            result_text += f"\n[Error al procesar imagen con IA: {e}]"
        finally:
            os.remove(temp_path)

    return {"lead_id": lead_id, "text": result_text}

# 4) Parseo de formularios anidados tipo Kommo
def parse_nested_form(form):
    result = {}

    for key, value in form.items():
        keys = key.replace("]", "").split("[")

        d = result
        for part in keys[:-1]:
            if part.isdigit():
                part = int(part)
            if isinstance(d, list):
                while len(d) <= part:
                    d.append({})
                d = d[part]
            else:
                if part not in d:
                    d[part] = [] if keys[keys.index(part) + 1].isdigit() else {}
                d = d[part]
        last_key = keys[-1]
        if last_key.isdigit():
            last_key = int(last_key)
            while len(d) <= last_key:
                d.append({})
            d[last_key] = value
        else:
            d[last_key] = value

    return result