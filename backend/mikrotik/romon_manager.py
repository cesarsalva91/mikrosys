from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

def cambiar_estado_romon(ip, puerto, usuario_api, clave_api, habilitar):
    try:
        pool = RouterOsApiPool(
            host=ip,
            username=usuario_api,
            password=clave_api,
            port=puerto,
            use_ssl=False,
            plaintext_login=True
        )
        api = pool.get_api()
        system = api.get_resource('/tool/romon')

        # Actualizar estado
        system.set(enabled='yes' if habilitar else 'no')

        pool.disconnect()
        estado = 'activado' if habilitar else 'desactivado'
        return True, f'ROMON {estado} correctamente'
    except RouterOsApiConnectionError:
        return False, 'Error de conexión con el router MikroTik'
    except Exception as e:
        return False, f'Error al cambiar estado de ROMON: {str(e)}'
