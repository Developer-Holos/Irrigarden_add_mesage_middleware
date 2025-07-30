import os
import requests

def add_message(lead_id: int, text: str):
    print(f"Iniciando add_message para lead_id: {lead_id}")
    
    token = os.getenv("TOKEN_KOMMO")
    subdomain = os.getenv("SUBDOMAIN_KOMMO")

    if not token or not subdomain:
        print("Error: Faltan variables de entorno")
        raise ValueError("TOKEN_KOMMO o SUBDOMAIN_KOMMO no está definida")

    url = f"https://{subdomain}.kommo.com/api/v4/leads/{lead_id}"
    print(f"URL: {url}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        print("Obteniendo datos del lead...")
        response = requests.get(url, headers=headers)
        print(f"Status code GET: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error en GET: {response.text}")
            return {"status": "error", "message": f"Error obteniendo lead: {response.status_code} - {response.text}"}

        data = response.json()
        custom_fields_values = data.get("custom_fields_values", [])
        print(f"Campos actuales: {custom_fields_values}")

        # Buscamos el campo personalizado
        field_found = False
        new_value = ""
        
        for field in custom_fields_values:
            if field.get("field_id") == 2959478:
                field_found = True
                print("Campo encontrado, actualizando valor")
                if field.get("values") and len(field["values"]) > 0:
                    new_value = field["values"][0]["value"] + "\n" + text
                else:
                    new_value = text
                break

        # Preparamos solo el campo que queremos actualizar
        if field_found:
            print(f"Actualizando campo existente con valor: {new_value}")
            custom_field_update = [{
                "field_id": 2959478,
                "values": [{"value": new_value}]
            }]
        else:
            print(f"Creando nuevo campo con valor: {text}")
            custom_field_update = [{
                "field_id": 2959478,
                "values": [{"value": text}]
            }]

        # Actualizamos solo el campo específico
        payload = {"custom_fields_values": custom_field_update}
        print(f"Payload del PATCH: {payload}")
        
        update_response = requests.patch(url, headers=headers, json=payload)
        print(f"Status code PATCH: {update_response.status_code}")
        print(f"Respuesta PATCH: {update_response.text}")
        
        if update_response.status_code not in (200, 201):
            return {
                "status": "error", 
                "message": f"Error actualizando lead: {update_response.status_code} - {update_response.text}"
            }

        return {"status": "ok", "message": "Mensaje agregado correctamente"}

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return {"status": "error", "message": f"Error de conexión: {str(e)}"}
    except ValueError as e:
        print(f"Error procesando JSON: {e}")
        return {"status": "error", "message": f"Error procesando JSON: {str(e)}"}
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"status": "error", "message": f"Error inesperado: {str(e)}"}