from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

def crear_grupo_router(ip, puerto, usuario_api, clave_api, nombre_grupo, politicas, skin=None):
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

        grupo = api.get_resource('/user/group')

        data = {
            'name': nombre_grupo,
            'policy': politicas
        }
        if skin:
            data['skin'] = skin

        grupo.add(**data)

        pool.disconnect()
        return True, f'Grupo \"{nombre_grupo}\" creado correctamente'
    except RouterOsApiConnectionError:
        return False, 'Error de conexión con el router MikroTik'
    except Exception as e:
        return False, f'Error al crear grupo: {str(e)}'
