from routeros_api import RouterOsApiPool

def configurar_snmp(ip, puerto, usuario_api, clave_api, configuracion):
    try:
        pool = RouterOsApiPool(ip, usuario_api, clave_api, port=puerto, plaintext_login=True)
        api = pool.get_api()

        # Activar o desactivar SNMP
        snmp = api.get_resource('/snmp')
        snmp.set(
            enabled='yes' if configuracion.get('habilitado') else 'no',
            trap_community=configuracion.get('trap_community', ''),
            trap_version=configuracion.get('trap_version', '1'),
            trap_generators=configuracion.get('trap_generators', '')
        )

        # Limpiar comunidades anteriores
        comunidades = api.get_resource('/snmp/community')
        for c in comunidades.get():
            comunidades.remove(id=c['id'])

        # Crear nuevas comunidades
        for c in configuracion.get('comunidades', []):
            nombre = c['nombre']
            addresses = ",".join(c.get('direcciones', []))
            comunidades.add(name=nombre, addresses=addresses, read_access='yes')

        pool.disconnect()
        return True, "Configuración SNMP aplicada correctamente"

    except Exception as e:
        return False, f"Error al aplicar configuración SNMP: {str(e)}"
