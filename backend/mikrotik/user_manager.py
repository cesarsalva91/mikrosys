from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

def crear_usuario_router(ip, puerto, usuario_api, clave_api, nuevo_usuario, clave, grupo):
    pool = None
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

        usuarios = api.get_resource('/user')
        usuarios.add(name=nuevo_usuario, password=clave, group=grupo)

        return True, f'Usuario \"{nuevo_usuario}\" creado correctamente'

    except RouterOsApiConnectionError:
        return False, 'Error de conexión con el router MikroTik'

    except Exception as e:
        mensaje_error = str(e)
        if 'already have user' in mensaje_error:
            return False, 'El usuario ya existe en el router.'
        return False, f'Error al crear usuario: {mensaje_error}'

    finally:
        if pool:
            try:
                pool.disconnect()
            except:
                pass  # Ignorar errores al cerrar conexión
