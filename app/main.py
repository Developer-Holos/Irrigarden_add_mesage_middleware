import os
from fastapi import FastAPI, Request, Form
from app.message_handler import parse_nested_form

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
