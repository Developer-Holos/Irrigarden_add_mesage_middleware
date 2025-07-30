import os
import requests

def add_message(lead_id: int, text: str):
   
    token = os.getenv("TOKEN_KOMMO")
    subdomain = os.getenv("SUBDOMAIN_KOMMO")

    if not token or not subdomain:
        raise ValueError("TOKEN_KOMMO o SUBDOMAIN_KOMMO no está definida")

    url = f"https://{subdomain}.kommo.com/api/v4/leads/{lead_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Primero obtenemos los datos actuales del lead
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"status": "error", "message": f"Error obteniendo lead: {response.status_code} - {response.text}"}

        data = response.json()
        custom_fields_values = data.get("custom_fields_values", [])

        # Buscamos el campo personalizado
        field_found = False
        for field in custom_fields_values:
            if field.get("field_id") == 2959478:
                field_found = True
                # Si ya existe un valor, concatenamos el nuevo texto
                if field.get("values") and len(field["values"]) > 0:
                    field["values"][0]["value"] = field["values"][0]["value"] + "\n" + text
                else:
                    field["values"] = [{"value": text}]
                break

        # Si no encontramos el campo, lo creamos
        if not field_found:
            custom_fields_values.append({
                "field_id": 2959478,
                "values": [{"value": text}]
            })

        # Actualizamos el lead con los nuevos valores
        payload = {"custom_fields_values": custom_fields_values}
        update_response = requests.patch(url, headers=headers, json=payload)
        
        if update_response.status_code not in (200, 201):
            return {
                "status": "error", 
                "message": f"Error actualizando lead: {update_response.status_code} - {update_response.text}"
            }

        return {"status": "ok", "message": "Mensaje agregado correctamente"}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Error de conexión: {str(e)}"}
    except ValueError as e:
        return {"status": "error", "message": f"Error procesando JSON: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Error inesperado: {str(e)}"}