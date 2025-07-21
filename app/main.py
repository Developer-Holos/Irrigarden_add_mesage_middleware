import os
import uvicorn
from fastapi import FastAPI, Request, Form
from app.message_handler import parse_nested_form, process_request_data
from app.kommo_service.validate_stage_kommo import validate_stage_kommo

app = FastAPI()

# Ruta webhook
@app.post("/add_message")
async def webhook(request: Request):
    try:
        print("Recibida petición")
        form = await request.form()
        print("Formulario recibido")
        data = parse_nested_form(form)
        print("Datos parseados:", data)
        msg = data["message"]["add"][0]
        lead_id = int(msg["entity_id"])
        print("Lead ID:", lead_id)

        try:
            is_valid = validate_stage_kommo(lead_id)
            print("Validación Kommo:", is_valid)
            if not is_valid:
                print("Lead no válido")
                return {"status": "error", "message": "Lead no está en la etapa o pipeline permitidos."}
        except Exception as e:
            print("Error en validación Kommo:", e)
            return {"status": "error", "message": f"Error validando etapa Kommo: {e}"}

        processed = await process_request_data(data)
        print(f"Datos procesados: {processed}")

        return {"status": "ok"}

    except Exception as e:
        print(f"Error procesando el webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)