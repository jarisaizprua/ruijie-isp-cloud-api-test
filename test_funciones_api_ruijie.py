import requests
import json
import os

class RuijieAPI:
    def __init__(self):
        self.config = self._load_config()
        self.base_url = f"https://{self.config['cloudserver']}"
        self.access_token = None

    def _load_config(self):
        ruta = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(ruta, 'r') as f:
            return json.load(f)

    def _ofuscar_serial(self, sn):
        """Ofuscar el serial mostrando asteriscos en los últimos 5 caracteres"""
        if not sn or len(sn) <= 5:
            return sn
        return sn[:-5] + '*' * 5

    def autenticar(self):
        """Paso 1: Obtener token de acceso"""
        url = f"{self.base_url}/service/api/oauth20/client/access_token"
        params = {"token": self.config['token_url']}
        payload = {
            "appid": self.config['appid'],
            "secret": self.config['secret']
        }
        
        try:
            response = requests.post(url, params=params, json=payload, timeout=10)
            data = response.json()
            if data.get("code") == 0:
                self.access_token = data.get("accessToken")
                print("✅ Autenticación exitosa.")
                return True
            print(f"❌ Error de autenticación: {data.get('msg')}")
        except Exception as e:
            print(f"❌ Error en conexión de login: {e}")
        return False

    def obtener_detalle_cuenta(self):
        """2.1.3 Get Account Detail"""
        url = f"{self.base_url}/service/api/org/account/info"
        params = {"access_token": self.access_token}
        
        res = requests.get(url, params=params)
        data = res.json()
        print("\n--- Info de Cuenta ---")
        print(json.dumps(data, indent=2))
        return data if data.get("code") == 0 else None

    def obtener_grupos_red(self):
        """2.2.1 Get Network Group List"""
        url = f"{self.base_url}/service/api/group/single/tree"
        params = {
            "access_token": self.access_token,
            "depth": "BUILDING"
        }
        
        res = requests.get(url, params=params)
        data = res.json()
        print("\n--- Grupos de Red ---")
        print(json.dumps(data, indent=2))
        return data

    def extraer_group_ids(self, grupos_data):
        """Extraer todos los group_ids de la estructura de grupos"""
        group_ids = []
        
        def extraer_recursivo(grupo):
            if isinstance(grupo, dict):
                if 'groupId' in grupo and grupo['groupId'] != 0:
                    group_ids.append({
                        'groupId': grupo['groupId'],
                        'name': grupo.get('name', ''),
                        'type': grupo.get('type', '')
                    })
                if 'subGroups' in grupo:
                    for subgrupo in grupo['subGroups']:
                        extraer_recursivo(subgrupo)
        
        if grupos_data.get('code') == 0:
            extraer_recursivo(grupos_data.get('groups', {}))
        
        return group_ids

    def obtener_estado_dispositivo(self, sn):
        """2.6.3 Get Device ON/OFF status"""
        url = f"{self.base_url}/service/api/device/{sn}"
        params = {"access_token": self.access_token}
        
        res = requests.get(url, params=params)
        data = res.json()
        print(f"\n--- Estado Dispositivo ({sn}) ---")
        if data.get("code") == 0:
            print(f"Status: {data.get('onlineStatus')}")
            print(f"Modelo: {data.get('productClass')}")
            # Agregar el SN a los datos para usarlo en el resumen
            data['sn'] = sn
            return data
        else:
            print(f"Error: {data.get('msg')}")
            return None

    def obtener_estado_puertos_gateway(self, sn):
        """2.6.4 Get Gateway Port status"""
        # Según la imagen, el endpoint es /service/api/gateway/intf/info/{sn}
        url = f"{self.base_url}/service/api/gateway/intf/info/{sn}"
        params = {"access_token": self.access_token}
        
        try:
            res = requests.get(url, params=params)
            data = res.json()
            print(f"\n--- Estado Puertos Gateway ({sn}) ---")
            print(json.dumps(data, indent=2))
            if data.get("code") == 0:
                return data.get("data", [])
            return None
        except Exception as e:
            print(f"❌ Error consultando puertos: {e}")
            return None

    def obtener_grupos_usuarios(self, group_id, page_index=0, page_size=100):
        """2.7.1 Get User Group List"""
        url = f"{self.base_url}/service/api/intl/usergroup/list/{group_id}"
        params = {
            "access_token": self.access_token,
            "pageIndex": page_index,
            "pageSize": page_size
        }
        
        try:
            res = requests.get(url, params=params)
            data = res.json()
            print(f"\n--- Grupos de Usuarios (Group ID: {group_id}) ---")
            if data.get("code") == 0:
                grupos = data.get("data", {}).get("list", [])
                total = data.get("data", {}).get("total", 0)
                print(f"Total de grupos: {total}")
                print(f"Grupos en esta página: {len(grupos)}")
                print(json.dumps(data, indent=2))
                return grupos
            else:
                print(f"Error: {data.get('msg')}")
        except Exception as e:
            print(f"❌ Error consultando grupos de usuarios: {e}")
        return []

    def obtener_clientes_conectados(self, group_id, page_index=1, page_size=100):
        """3.0 Get Current Connected Clients"""
        url = f"{self.base_url}/service/api/open/v1/dev/user/current-user"
        params = {
            "access_token": self.access_token,
            "group_id": group_id,  # Parámetro obligatorio
            "page_index": page_index,
            "page_size": page_size
        }
        
        try:
            res = requests.get(url, params=params)
            data = res.json()
            print(f"\n--- Clientes Conectados (Group ID: {group_id}, Página {page_index}) ---")
            if data.get("code") == 0:
                # Los datos vienen directamente en data["list"], no en data["data"]["list"]
                clientes = data.get("list", [])
                total = data.get("totalCount", 0)
                print(f"Total de clientes: {total}")
                print(f"Clientes en esta página: {len(clientes)}")
                print(json.dumps(data, indent=2))
                return clientes
            else:
                print(f"Error: {data.get('msg')}")
        except Exception as e:
            print(f"❌ Error consultando clientes conectados: {e}")
        return []

    def imprimir_resumen(self, cuenta_data=None, dispositivo_data=None, puertos_data=None, clientes_data=None):
        """Imprimir resumen formateado con información relevante"""
        print("\n" + "="*80)
        print(" "*25 + "RESUMEN DE CONEXIÓN Y RED")
        print("="*80)
        
        # === INFORMACIÓN DE CUENTA ===
        if cuenta_data:
            print("\n📋 INFORMACIÓN DE CUENTA:")
            print(f"   • Usuario: {cuenta_data.get('userName', 'N/A')}")
            print(f"   • Email: {cuenta_data.get('email', 'N/A')}")
            print(f"   • Compañía: {cuenta_data.get('company', 'N/A')}")
            print(f"   • Rol: {cuenta_data.get('role', 'N/A')}")
            print(f"   • Zona Horaria: {cuenta_data.get('timeZone', 'N/A')}")
        
        # === INFORMACIÓN DEL DISPOSITIVO ===
        if dispositivo_data:
            sn_ofuscado = self._ofuscar_serial(dispositivo_data.get('sn', 'N/A'))
            print("\n🔌 DISPOSITIVO PRINCIPAL:")
            print(f"   • Estado: {'🟢 ONLINE' if dispositivo_data.get('onlineStatus') == 'ON' else '🔴 OFFLINE'}")
            print(f"   • Modelo: {dispositivo_data.get('productClass', 'N/A')}")
            print(f"   • Serial Number: {sn_ofuscado}")
        
        # === INFORMACIÓN DE PUERTOS ===
        if puertos_data:
            print("\n🌐 PUERTOS DEL ROUTER:")
            wan_port = None
            lan_ports = []
            
            for puerto in puertos_data:
                if puerto.get('type') == 'WAN':
                    wan_port = puerto
                elif puerto.get('type') == 'LAN':
                    lan_ports.append(puerto)
            
            # Puerto WAN
            if wan_port:
                print(f"\n   WAN ({wan_port.get('alias', 'N/A')}):")
                print(f"      ├─ Estado: {'🟢 Conectado' if wan_port.get('linestatus') == 'true' else '🔴 Desconectado'}")
                print(f"      ├─ IP: {wan_port.get('ipAddr', 'N/A')}")
                print(f"      ├─ Máscara: {wan_port.get('ipMask', 'N/A')}")
                print(f"      ├─ Gateway: {wan_port.get('nextHop', 'N/A')}")
                print(f"      ├─ Velocidad: {wan_port.get('speed', 'N/A')}")
                print(f"      └─ Tipo IP: {wan_port.get('ipType', 'N/A').upper()}")
            
            # Puertos LAN
            if lan_ports:
                print(f"\n   Puertos LAN:")
                for lan in lan_ports:
                    estado = '🟢' if lan.get('linestatus') == 'true' else '🔴'
                    dhcp_info = lan.get('dhcpInfo', {})
                    print(f"      • {lan.get('alias', 'N/A')}: {estado} | IP: {lan.get('ipAddr', 'N/A')} | "
                          f"DHCP: {dhcp_info.get('status', 'N/A')} | "
                          f"Pool: {dhcp_info.get('startIp', 'N/A')} - {dhcp_info.get('endIp', 'N/A')}")
        
        # === CLIENTES CONECTADOS ===
        if clientes_data:
            print(f"\n👥 CLIENTES CONECTADOS ({len(clientes_data)} dispositivos):")
            print("=" * 140)
            
            # Tabla de clientes conectados
            # Encabezado
            print(f"{'#':<3} {'Nombre':<18} {'IP':<15} {'MAC':<17} {'Tipo Conexión':<13} {'Banda':<6} {'RSSI':<8} {'Tiempo Online':<15} {'Tráfico Total':<15}")
            print("=" * 140)
            
            for i, cliente in enumerate(clientes_data, 1):
                # Calcular tiempo de conexión
                tiempo_online = cliente.get('activeSec', 0)
                horas = tiempo_online // 3600
                minutos = (tiempo_online % 3600) // 60
                segundos = tiempo_online % 60
                tiempo_str = f"{horas}h {minutos}m {segundos}s"
                
                # Convertir flujo de datos a MB
                flow_total_mb = cliente.get('flowUpDown', 0) / (1024 * 1024)
                
                # Nombre del dispositivo
                nombre = cliente.get('userName', cliente.get('alias', 'Desconocido'))
                if nombre == '*':
                    nombre = cliente.get('alias', 'Sin nombre')
                nombre = nombre[:17]  # Truncar si es muy largo
                
                # IP y MAC
                ip = cliente.get('ip', 'N/A')
                mac = cliente.get('mac', 'N/A')
                
                # Tipo de conexión
                tipo_conn = cliente.get('connectType', 'N/A').upper()
                
                # Banda y RSSI (solo para wireless)
                banda = cliente.get('band', '-') if tipo_conn == 'WIRELESS' else '-'
                rssi = f"{cliente.get('rssi', '-')} dBm" if tipo_conn == 'WIRELESS' and cliente.get('rssi') else '-'
                
                # Tráfico
                trafico_str = f"{flow_total_mb:.2f} MB"
                
                print(f"{i:<3} {nombre:<18} {ip:<15} {mac:<17} {tipo_conn:<13} {banda:<6} {rssi:<8} {tiempo_str:<15} {trafico_str:<15}")
            
            print("=" * 140)
            
            # Tabla detallada de información WiFi (solo para clientes wireless)
            clientes_wifi = [c for c in clientes_data if c.get('connectType') == 'wireless']
            if clientes_wifi:
                print(f"\n📶 DETALLES DE CONEXIONES WIFI:")
                print("=" * 120)
                print(f"{'Nombre':<18} {'SSID':<20} {'Canal':<8} {'Fabricante':<20} {'Upload':<12} {'Download':<12} {'Pérdida %':<10}")
                print("=" * 120)
                
                for cliente in clientes_wifi:
                    nombre = cliente.get('userName', cliente.get('alias', 'Desconocido'))
                    if nombre == '*':
                        nombre = cliente.get('alias', 'Sin nombre')
                    nombre = nombre[:17]
                    
                    ssid = cliente.get('ssid', 'N/A')[:19]
                    canal = cliente.get('channel', 'N/A')
                    fabricante = cliente.get('manufacturer', 'N/A')[:19]
                    
                    # Tráfico
                    flow_up_mb = cliente.get('flowUp', 0) / (1024 * 1024)
                    flow_down_mb = cliente.get('flowDown', 0) / (1024 * 1024)
                    upload_str = f"{flow_up_mb:.2f} MB"
                    download_str = f"{flow_down_mb:.2f} MB"
                    
                    perdida = f"{cliente.get('pktLoseRate', 0)}%"
                    
                    print(f"{nombre:<18} {ssid:<20} {canal:<8} {fabricante:<20} {upload_str:<12} {download_str:<12} {perdida:<10}")
                
                print("=" * 120)
            
            # Resumen de estadísticas
            print(f"\n📊 ESTADÍSTICAS GENERALES:")
            total_trafico = sum(c.get('flowUpDown', 0) for c in clientes_data) / (1024 * 1024)
            total_upload = sum(c.get('flowUp', 0) for c in clientes_data) / (1024 * 1024)
            total_download = sum(c.get('flowDown', 0) for c in clientes_data) / (1024 * 1024)
            
            print(f"   • Total de dispositivos: {len(clientes_data)}")
            print(f"   • Conexiones WiFi: {len(clientes_wifi)}")
            print(f"   • Conexiones cableadas: {len(clientes_data) - len(clientes_wifi)}")
            print(f"   • Tráfico total de red: {total_trafico:.2f} MB")
            print(f"   • Tráfico de subida: {total_upload:.2f} MB")
            print(f"   • Tráfico de bajada: {total_download:.2f} MB")
        
        print("\n" + "="*80)
        print(" "*30 + "FIN DEL RESUMEN")
        print("="*80 + "\n")

if __name__ == "__main__":
    api = RuijieAPI()
    
    if api.autenticar():
        # Variables para almacenar datos
        cuenta_info = None
        dispositivo_info = None
        puertos_info = None
        clientes_info = None
        
        # Ejecución de cada bloque funcional
        cuenta_info = api.obtener_detalle_cuenta()
        grupos_data = api.obtener_grupos_red()
        
        # Extraer group_ids disponibles
        group_ids = api.extraer_group_ids(grupos_data)
        print(f"\n--- Group IDs Disponibles ---")
        for grupo in group_ids:
            print(f"  - {grupo['name']} (ID: {grupo['groupId']}, Tipo: {grupo['type']})")
        
        sn_objetivo = api.config.get("device_sn")
        if sn_objetivo:
            dispositivo_info = api.obtener_estado_dispositivo(sn_objetivo)
            puertos_info = api.obtener_estado_puertos_gateway(sn_objetivo)
        else:
            print("\n⚠️ No se proporcionó un SN en config.json para las pruebas de dispositivo.")
        
        # Usar el primer group_id tipo BUILDING encontrado o el especificado en config
        group_id_objetivo = api.config.get("group_id")
        
        if not group_id_objetivo and group_ids:
            # Buscar un grupo tipo BUILDING
            for grupo in group_ids:
                if grupo['type'] == 'BUILDING':
                    group_id_objetivo = grupo['groupId']
                    print(f"\n✅ Usando group_id automático: {group_id_objetivo} ({grupo['name']})")
                    break
            
            # Si no hay BUILDING, usar el último disponible
            if not group_id_objetivo:
                group_id_objetivo = group_ids[-1]['groupId']
                print(f"\n✅ Usando group_id: {group_id_objetivo} ({group_ids[-1]['name']})")
        
        if group_id_objetivo:
            # Obtener grupos de usuarios
            api.obtener_grupos_usuarios(group_id_objetivo)
            
            # Obtener clientes conectados
            clientes_info = api.obtener_clientes_conectados(group_id_objetivo)
        else:
            print("\n⚠️ No se pudo determinar un group_id válido.")
        
        # Imprimir resumen final
        api.imprimir_resumen(
            cuenta_data=cuenta_info,
            dispositivo_data=dispositivo_info,
            puertos_data=puertos_info,
            clientes_data=clientes_info
        )
