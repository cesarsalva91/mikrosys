from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

def cambiar_estado_romon(ip, puerto, usuario_api, clave_api, habilitar, secret=None):
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
        romon = api.get_resource('/tool/romon')

        if habilitar:
            romon.set(enabled='yes')
        else:
            romon.set(enabled='no')

        pool.disconnect()
        return True, f"ROMON {'activado' if habilitar else 'desactivado'} correctamente"
    except RouterOsApiConnectionError:
        return False, 'Error de conexión con el router MikroTik'
    except Exception as e:
        return False, f'Error al cambiar estado de ROMON: {str(e)}'


def aplicar_secret_romon(ip, puerto, usuario_api, clave_api, secret):
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
        romon = api.get_resource('/tool/romon')

        romon.set(secrets=secret)  

        pool.disconnect()
        return True, "Contraseña (secret) aplicada correctamente"
    except RouterOsApiConnectionError:
        return False, 'Error de conexión con el router MikroTik'
    except Exception as e:
        return False, f'Error al aplicar secret: {str(e)}'
