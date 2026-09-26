import requests
import json
import os

def conectar_ruijie():
    # 1. Cargar credenciales desde el archivo local
    ruta_config = os.path.join(os.path.dirname(__file__), 'config.json')
    
    try:
        with open(ruta_config, 'r') as f:
            config = json.load(f)
            
        # 2. Configurar la URL de acceso según tu imagen
        # La URL base es https://cloud-eu.ruijienetworks.com
        base_url = config['cloudserver'].strip('/')
        endpoint = "/service/api/oauth20/client/access_token"
        
        # El parámetro 'token' en la URL suele ser el AppID en esta API
        url_completa = f"https://{base_url}{endpoint}?token={config['token_url']}"
        
        # 3. Preparar el cuerpo (Payload)
        payload = {
            "appid": config['appid'],
            "secret": config['secret']
        }
        
        headers = {
            "Content-Type": "application/json"
        }

        print(f"🚀 Conectando a Ruijie Cloud...")
        print(f"🔗 URL: {url_completa}")

        # 4. Realizar la petición POST
        response = requests.post(url_completa, json=payload, headers=headers, timeout=15)
        
        # 5. Procesar la respuesta
        resultado = response.json()
        
        if resultado.get("code") == 0:
            print("\n✅ ¡CONEXIÓN EXITOSA!")
            print(f"📝 Mensaje: {resultado.get('msg')}")
            print(f"🔑 AccessToken: {resultado.get('accessToken')}")
            
            # Opcional: Guardar el token para usarlo en otras llamadas
            with open('token_actual.txt', 'w') as f:
                f.write(resultado.get('accessToken'))
            print("💾 Token guardado en 'token_actual.txt'")
            
        else:
            print(f"\n❌ Error de la API")
            print(f"Código: {resultado.get('code')}")
            print(f"Mensaje: {resultado.get('msg')}")
            if resultado.get("code") == 5:
                print("💡 Tip: Revisa que el 'Secret' sea el correcto (dale al botón 'Copy' en tu panel).")

    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'config.json'.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    conectar_ruijie()