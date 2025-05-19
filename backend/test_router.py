from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

def conectar_a_router(ip, puerto, usuario, clave):
    try:
        api_pool = RouterOsApiPool(
            host=ip,
            username=usuario,
            password=clave,
            port=puerto,
            use_ssl=False,
            plaintext_login=True
        )
        api = api_pool.get_api()
        print(f" Conexión exitosa a {ip}:{puerto}")
        return api
    except RouterOsApiConnectionError as e:
        print(f" Error de conexión: {e}")
        return None

# Ejemplo de uso (luego se reemplazará por datos desde la DB)
if __name__ == '__main__':
    api = conectar_a_router('192.168.240.137', 8728, 'admin', 'admin')
    if api:
        # Por ejemplo, obtener la lista de interfaces
        interfaces = api.get_resource('/interface').get()
        for iface in interfaces:
            print(f"{iface['name']} - {iface['type']}")
