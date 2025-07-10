import os
from fastapi import FastAPI, Request, Form
from app.message_handler import parse_nested_form, process_request_data

app = FastAPI()

# Ruta webhook
@app.post("/add_message")
async def webhook(request: Request):
    try:
        form = await request.form()
        data = parse_nested_form(form)
        processed = await process_request_data(data)
        print(f"Datos procesados: {processed}")

        return {"status": "ok"}
    
    except Exception as e:
        print(f"Error procesando el webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)