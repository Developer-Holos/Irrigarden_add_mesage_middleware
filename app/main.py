import os
from fastapi import FastAPI, Request, Form
from app.redis_client import store_message_in_redis, get_messages_for_lead, delete_messages_for_lead, set_lead_timer, lead_timer_exists, check_expired_leads
from app.message_handler import process_request_data, parse_nested_form
import asyncio

app = FastAPI()

# Ruta webhook
@app.post("/webhook")
async def webhook(request: Request):
    try:
        form = await request.form()
        form_dict = parse_nested_form(form)
        print("Datos recibidos:", form_dict)
        # message = await process_request_data(form_dict)

        return {"status": "ok"}
    
    except Exception as e:
        print(f"Error procesando el webhook: {e}")
        return {"status": "error", "message": str(e)}
