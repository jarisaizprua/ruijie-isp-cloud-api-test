# Ruijie ISP Cloud API - Scripts de Prueba de Conexión

Scripts en Python para **probar la conexión y autenticación** con la API de **Ruijie ISP Cloud** (`cloud-eu.ruijienetworks.com`), la plataforma de Ruijie orientada a proveedores de servicios de internet (ISP). Permiten validar credenciales mediante OAuth2 y consultar información de cuenta, dispositivos, grupos de red y clientes conectados.

> Este proyecto es de **prueba/diagnóstico** (test de conectividad y de los distintos endpoints de la API), no una integración de producción.

## 📁 Contenido

- `test_conexion_api_ruijie.py` — Script simple para probar la **conexión y autenticación** contra la API de Ruijie ISP Cloud (obtiene y guarda el `accessToken`).
- `test_funciones_api_ruijie.py` — Clase `RuijieAPI` que, una vez validada la conexión, prueba distintos endpoints:
  - Autenticación (OAuth2)
  - Información de cuenta
  - Grupos de red (árbol de grupos)
  - Estado de dispositivos (online/offline)
  - Estado de puertos del gateway (WAN/LAN)
  - Grupos de usuarios
  - Clientes conectados (con detalle de tráfico y WiFi)
  - Resumen formateado en consola

## ⚙️ Requisitos

- Python 3.7+
- Librería `requests`

```bash
pip install requests
```

## 🔧 Configuración

1. Copia la plantilla de configuración:

   ```bash
   cp config.json.example config.json
   ```

2. Edita `config.json` con tus credenciales reales de Ruijie Cloud:

   ```json
   {
     "cloudserver": "cloud-eu.ruijienetworks.com",
     "token_url": "TU_TOKEN_URL",
     "appid": "TU_APPID",
     "secret": "TU_SECRET",
     "device_sn": "SN_DEL_DISPOSITIVO",
     "group_id": "ID_DEL_GRUPO"
   }
   ```

   > ⚠️ **Importante:** `config.json` contiene credenciales sensibles y está excluido del repositorio mediante `.gitignore`. Nunca lo subas a GitHub.

## ▶️ Uso

**Probar solo la conexión / autenticación:**

```bash
python test_conexion_api_ruijie.py
```

Guarda el token obtenido en `token_actual.txt` (también ignorado por git).

**Ejecutar el flujo completo de consultas:**

```bash
python test_funciones_api_ruijie.py
```

Esto autentica, consulta la cuenta, los grupos de red, el estado del dispositivo (si se definió `device_sn`), los puertos del gateway, los grupos de usuarios y los clientes conectados, mostrando un resumen final en consola.

## 🔐 Seguridad

- No compartas ni subas `config.json` ni `token_actual.txt`.
- Los números de serie se muestran ofuscados (últimos 5 caracteres) en el resumen impreso.
- Considera usar variables de entorno en lugar de `config.json` para entornos de producción.

---
Desarrollado por Jaris Aizprúa B. — Diciembre 2025
