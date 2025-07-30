import os
import uvicorn
from fastapi import FastAPI, Request, Form
from app.message_handler import parse_nested_form, process_request_data
from app.kommo_service.validate_stage_kommo import validate_stage_kommo
from app.kommo_service.add_message import add_message

app = FastAPI()

# Ruta webhook
@app.post("/add_message")
async def webhook(request: Request):
    try:
        form = await request.form()
        data = parse_nested_form(form)
        msg = data["message"]["add"][0]
        lead_id = int(msg["entity_id"])

        try:
            is_valid = validate_stage_kommo(lead_id)
            if not is_valid:
                return {"status": "error", "message": "Lead no está en la etapa o pipeline permitidos."}
        except Exception as e:
            return {"status": "error", "message": f"Error validando etapa Kommo: {e}"}

        processed = await process_request_data(data)
        
        add_message_result = add_message(processed["lead_id"], processed["text"])

        print(f"Mensaje agregado correctamente al lead {lead_id}")

        return {"status": "ok"}

    except Exception as e:
        print(f"Error procesando el webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)