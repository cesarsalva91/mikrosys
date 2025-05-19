from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

def obtener_usuarios_y_grupos(ip, puerto, usuario_api, clave_api):
    try:
        pool = RouterOsApiPool(ip, usuario_api, clave_api, port=puerto, plaintext_login=True)
        api = pool.get_api()

        usuarios = api.get_resource('/user').get()
        grupos = api.get_resource('/user/group').get()

        pool.disconnect()
        return True, {'usuarios': usuarios, 'grupos': grupos}

    except RouterOsApiConnectionError:
        return False, 'Error de conexión con el router'
    except Exception as e:
        return False, f'Error: {str(e)}'

def eliminar_usuario(ip, puerto, usuario_api, clave_api, nombre_usuario):
    try:
        pool = RouterOsApiPool(ip, usuario_api, clave_api, port=puerto, plaintext_login=True)
        api = pool.get_api()
        usuarios = api.get_resource('/user')

        eliminados = 0
        for u in usuarios.get():
            if u['name'] == nombre_usuario:
                usuarios.remove(id=u['id'])
                eliminados += 1

        pool.disconnect()

        if eliminados > 0:
            return True, f'Se eliminaron {eliminados} usuario(s) con nombre "{nombre_usuario}"'
        else:
            return False, f'No se encontraron usuarios con nombre "{nombre_usuario}"'

    except Exception as e:
        return False, f'Error al eliminar usuario: {str(e)}'

def eliminar_grupo(ip, puerto, usuario_api, clave_api, nombre_grupo):
    try:
        pool = RouterOsApiPool(ip, usuario_api, clave_api, port=puerto, plaintext_login=True)
        api = pool.get_api()
        grupos = api.get_resource('/user/group')

        eliminados = 0
        for g in grupos.get():
            if g['name'] == nombre_grupo:
                grupos.remove(id=g['id'])
                eliminados += 1

        pool.disconnect()

        if eliminados > 0:
            return True, f'Se eliminaron {eliminados} grupo(s) con nombre "{nombre_grupo}"'
        else:
            return False, f'No se encontraron grupos con nombre "{nombre_grupo}"'

    except Exception as e:
        return False, f'Error al eliminar grupo: {str(e)}'

