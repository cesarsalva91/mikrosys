from routeros_api import RouterOsApiPool

def configurar_ntp(ip, puerto, usuario_api, clave_api, ntp_primario, ntp_secundario=None, habilitado=True):
    try:
        pool = RouterOsApiPool(ip, usuario_api, clave_api, port=puerto, plaintext_login=True)
        api = pool.get_api()

        recursos_ntp = ['/system/ntp/client', '/system/ntp']  # probar ambos
        ntp = None

        for recurso in recursos_ntp:
            try:
                ntp = api.get_resource(recurso)
                ntp.set(
                    enabled='yes' if habilitado else 'no',
                    primary_ntp=ntp_primario,
                    secondary_ntp=ntp_secundario if ntp_secundario else '0.0.0.0'
                )
                pool.disconnect()
                estado = "activado" if habilitado else "desactivado"
                return True, f'NTP {estado} correctamente usando {recurso}'
            except Exception:
                continue  # probá el siguiente recurso si este falla

        return False, 'No se pudo configurar NTP: el recurso no fue encontrado en el router'

    except Exception as e:
        return False, f'Error al configurar NTP: {str(e)}'