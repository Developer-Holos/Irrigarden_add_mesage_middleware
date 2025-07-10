import os #Accede a variables de entorno y funciones del sistema operativo
import aiofiles #Permite leer y escribir archivos de forma asíncrona.
import aiohttp #Permite realizar solicitudes HTTP de forma asíncrona.
import requests #Permite realizar solicitudes HTTP de forma sincrónica.
from dotenv import load_dotenv #Carga las variables de entorno desde un archivo .env
# load_dotenv()


async def download_audio_file(url: str, path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to download file: {response.status}")
            async with aiofiles.open(path, 'wb') as f:
                await f.write(await response.read())


async def transcribe_audio(file_path: str):
    api_key = os.getenv("OPENAI_API_KEY")

    with open(file_path, "rb") as audio_file:
        response = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={
                "Authorization": f"Bearer {api_key}"
            },
            files={
                "file": audio_file,
                "model": (None, "whisper-1")
            }
        )

    if response.status_code != 200:
        raise Exception(f"Error transcribiendo: {response.status_code}, {response.text}")
    
    return response.json().get("text")


# async def process_request_data(form_data: dict):
#     try:
#         message_data = form_data["message"]["add"][0]
#         lead_id = int(message_data["entity_id"])
#         audio_url = message_data.get("attachment", {}).get("link")
#         text_message = message_data.get("text", "")

#         access_token = os.getenv("KOMMO_API_KEY")
#         subdominio = os.getenv("SUBDOMINIO", "holos")

#         lead_details = await get_lead_details(lead_id, access_token, subdominio)
#         pipeline_id = lead_details.get("pipeline_id")
#         status_id = lead_details.get("status_id")

#         if pipeline_id == 5220299 and status_id == 46659818:
#             transcription = ""
#             if audio_url:
#                 audio_path = f"/tmp/{lead_id}.m4a"
#                 await download_audio_file(audio_url, audio_path)
#                 transcription = await transcribe_audio(audio_path)
#                 os.remove(audio_path)

#             full_text = f"{text_message} {transcription}".strip()
#             return {
#                 "lead_id": lead_id,
#                 "text": full_text
#             }

#         return None

#     except Exception as e:
#         print(f"❌ Error procesando request: {e}")
#         return None
    

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