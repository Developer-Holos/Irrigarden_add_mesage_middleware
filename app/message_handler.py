import os  # Accede a variables de entorno y funciones del sistema operativo
import aiofiles  # Permite leer y escribir archivos de forma asíncrona
import aiohttp  # Permite realizar solicitudes HTTP de forma asíncrona
import cv2
import numpy as np
import pytesseract
from fastapi import FastAPI, Request
from dotenv import load_dotenv  # Carga las variables de entorno desde un .env

load_dotenv()  # Si usas .env para tus claves

# 1) Función genérica de descarga
async def download_file(url: str, path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            async with aiofiles.open(path, 'wb') as f:
                await f.write(await resp.read())
    return path

# 2) OCR robusto para capturas/tablas
def ocr_from_image(path: str) -> str:
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    data = pytesseract.image_to_data(
        thresh,
        lang="spa+eng",
        config="--psm 6",
        output_type=pytesseract.Output.DICT
    )

    from collections import defaultdict
    rows = defaultdict(list)
    for i, txt in enumerate(data["text"]):
        txt = txt.strip()
        if not txt:
            continue
        line = data["line_num"][i]
        x = data["left"][i]
        rows[line].append((x, txt))

    lines = []
    for ln in sorted(rows):
        words = sorted(rows[ln], key=lambda w: w[0])
        line_text = " ".join(w for _, w in words)
        lines.append(line_text)

    return "\n".join(lines)

# 3) Tu función principal de negocio, ahora sin audio/CSV
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

        # descarga + OCR
        await download_file(url, temp_path)
        ocr_text = ocr_from_image(temp_path)
        os.remove(temp_path)

        result_text += f"\n[OCR de imagen:]\n{ocr_text}"

    return {"lead_id": lead_id, "text": result_text}

def parse_nested_form(form):
    result = {}

    for key, value in form.items():
        # Ej: message[add][0][text] → ['message', 'add', '0', 'text']
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