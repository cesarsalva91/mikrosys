from routeros_api import RouterOsApiPool

def configurar_ntp(ip, puerto, usuario_api, clave_api, ntp_primario, ntp_secundario=None):
    try:
        pool = RouterOsApiPool(ip, usuario_api, clave_api, port=puerto, plaintext_login=True)
        api = pool.get_api()

        ntp = api.get_resource('/system/ntp/client')

        ntp.set(
            enabled='yes',
            primary_ntp=ntp_primario,
            secondary_ntp=ntp_secundario if ntp_secundario else '0.0.0.0'
        )

        pool.disconnect()
        return True, 'NTP configurado correctamente'

    except Exception as e:
        return False, f'Error al configurar NTP: {str(e)}'
