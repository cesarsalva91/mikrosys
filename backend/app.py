from flask import Flask, request, jsonify
from flask_cors import CORS
from db import obtener_conexion

from mikrotik.user_manager import crear_usuario_router
from mikrotik.romon_manager import cambiar_estado_romon
from mikrotik.group_manager import crear_grupo_router
from mikrotik.skin_uploader import subir_skin_a_router
from mikrotik.ntp_manager import configurar_ntp

import os
import tempfile

from mikrotik.delete_manager import (
    obtener_usuarios_y_grupos,
    eliminar_usuario,
    eliminar_grupo
)

app = Flask(__name__)
CORS(app)

@app.route('/api/acciones', methods=['GET'])
def obtener_acciones():
    acciones = [
        "1 - Cargar grupo de usuario",
        "2 - Crear usuarios",
        "3 - Eliminar grupo o usuario (por nombre exacto)",
        "4 - Modificar NTP",
        "5 - Modificar SNMP",
        "6 - Activar/Desactivar ROMON",
        "7 - Cambiar ID de equipo",
        "8 - Crear/Eliminar address list",
        "9 - Crear/Eliminar filter rules - raw rules"
    ]
    return jsonify({'acciones': acciones})

@app.route('/api/equipos', methods=['GET'])
def listar_equipos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, ip, puerto FROM equipos")
    equipos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(equipos)

@app.route('/api/crear-usuario', methods=['POST'])
def crear_usuario():
    try:
        data = request.get_json()
        id_equipo = data['idEquipo']
        nuevo_usuario = data['nombre']
        clave = data['clave']
        grupo = data['grupo']

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT ip, puerto, usuario, contrasena FROM equipos WHERE id = %s", (id_equipo,))
        equipo = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not equipo:
            return jsonify({'mensaje': 'Equipo no encontrado'}), 404

        exito, mensaje = crear_usuario_router(
            ip=equipo['ip'],
            puerto=equipo['puerto'],
            usuario_api=equipo['usuario'],
            clave_api=equipo['contrasena'],
            nuevo_usuario=nuevo_usuario,
            clave=clave,
            grupo=grupo
        )

        return jsonify({'mensaje': mensaje}), 200 if exito else 400

    except Exception as e:
        return jsonify({'mensaje': f'Error inesperado: {str(e)}'}), 500

@app.route('/api/romon', methods=['POST'])
def toggle_romon():
    data = request.get_json()
    id_equipo = data['idEquipo']
    habilitar = data['habilitar']
    secret_romon = data.get('secret', None)

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT ip, puerto, usuario, contrasena FROM equipos WHERE id = %s", (id_equipo,))
    equipo = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not equipo:
        return jsonify({'mensaje': 'Equipo no encontrado'}), 404

    exito, mensaje = cambiar_estado_romon(
        ip=equipo['ip'],
        puerto=equipo['puerto'],
        usuario_api=equipo['usuario'],
        clave_api=equipo['contrasena'],
        habilitar=habilitar,
        secret=secret_romon
    )

    return jsonify({'mensaje': mensaje}), 200 if exito else 400

@app.route('/api/aplicar-secret', methods=['POST'])
def aplicar_secret_romon_endpoint():
    data = request.get_json()
    id_equipo = data['idEquipo']
    secret = data['secret']

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT ip, puerto, usuario, contrasena FROM equipos WHERE id = %s", (id_equipo,))
    equipo = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not equipo:
        return jsonify({'mensaje': 'Equipo no encontrado'}), 404

    from mikrotik.romon_manager import aplicar_secret_romon  # asegurate que esté importado

    exito, mensaje = aplicar_secret_romon(
        ip=equipo['ip'],
        puerto=equipo['puerto'],
        usuario_api=equipo['usuario'],
        clave_api=equipo['contrasena'],
        secret=secret
    )

    return jsonify({'mensaje': mensaje}), 200 if exito else 500



@app.route('/api/crear-grupo', methods=['POST'])
def crear_grupo():
    data = request.get_json()
    id_equipo = data['idEquipo']
    nombre = data['nombre']
    politicas = data['politicas']
    skin = data.get('skin', None)

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT ip, puerto, usuario, contrasena FROM equipos WHERE id = %s", (id_equipo,))
    equipo = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not equipo:
        return jsonify({'mensaje': 'Equipo no encontrado'}), 404

    exito, mensaje = crear_grupo_router(
        ip=equipo['ip'],
        puerto=equipo['puerto'],
        usuario_api=equipo['usuario'],
        clave_api=equipo['contrasena'],
        nombre_grupo=nombre,
        politicas=politicas,
        skin=skin
    )

    return jsonify({'mensaje': mensaje}), 200 if exito else 400

@app.route('/api/subir-skin', methods=['POST'])
def subir_skin():
    id_equipo = request.form.get('idEquipo')
    nombre_skin = request.form.get('nombreSkin')
    archivo = request.files.get('archivoSkin')


    if not archivo or not nombre_skin:
        return jsonify({'mensaje': 'Faltan datos'}), 400

    if not archivo.filename.endswith(('.zip', '.json')):
        return jsonify({'mensaje': 'Formato de archivo no permitido'}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT ip, puerto, usuario, contrasena FROM equipos WHERE id = %s", (id_equipo,))
    equipo = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not equipo:
        return jsonify({'mensaje': 'Equipo no encontrado'}), 404

    ruta_skin = os.path.join(tempfile.gettempdir(), archivo.filename)
    archivo.save(ruta_skin)

    exito, mensaje = subir_skin_a_router(
        ip=equipo['ip'],
        puerto_ssh=22,
        usuario=equipo['usuario'],
        clave=equipo['contrasena'],
        archivo_skin=ruta_skin,
        nombre_skin=nombre_skin
    )

    os.remove(ruta_skin)

    return jsonify({'mensaje': mensaje}), 200 if exito else 500

@app.route('/api/obtener-usuarios-grupos', methods=['POST'])
def obtener_datos_eliminacion():
    data = request.get_json()
    id_equipo = data['idEquipo']

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT ip, puerto, usuario, contrasena FROM equipos WHERE id = %s", (id_equipo,))
    equipo = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not equipo:
        return jsonify({'mensaje': 'Equipo no encontrado'}), 404

    exito, resultado = obtener_usuarios_y_grupos(
        ip=equipo['ip'],
        puerto=equipo['puerto'],
        usuario_api=equipo['usuario'],
        clave_api=equipo['contrasena']
    )

    return jsonify(resultado if exito else {'mensaje': resultado}), 200 if exito else 500

@app.route('/api/eliminar', methods=['POST'])
def eliminar_objeto():
    data = request.get_json()
    id_equipo = data['idEquipo']
    tipo = data['tipo']
    nombre = data['nombre']

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT ip, puerto, usuario, contrasena FROM equipos WHERE id = %s", (id_equipo,))
    equipo = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not equipo:
        return jsonify({'mensaje': 'Equipo no encontrado'}), 404

    if tipo == "usuario":
        exito, mensaje = eliminar_usuario(equipo['ip'], equipo['puerto'], equipo['usuario'], equipo['contrasena'], nombre)
    elif tipo == "grupo":
        exito, mensaje = eliminar_grupo(equipo['ip'], equipo['puerto'], equipo['usuario'], equipo['contrasena'], nombre)
    else:
        return jsonify({'mensaje': 'Tipo inválido'}), 400

    return jsonify({'mensaje': mensaje}), 200 if exito else 500

@app.route('/api/modificar-ntp', methods=['POST'])
def modificar_ntp():
    data = request.get_json()
    id_equipo = data['idEquipo']
    ntp_primario = data['ntpPrimario']
    ntp_secundario = data.get('ntpSecundario', None)

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT ip, puerto, usuario, contrasena FROM equipos WHERE id = %s", (id_equipo,))
    equipo = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not equipo:
        return jsonify({'mensaje': 'Equipo no encontrado'}), 404

    exito, mensaje = configurar_ntp(
        ip=equipo['ip'],
        puerto=equipo['puerto'],
        usuario_api=equipo['usuario'],
        clave_api=equipo['contrasena'],
        ntp_primario=ntp_primario,
        ntp_secundario=ntp_secundario
    )

    return jsonify({'mensaje': mensaje}), 200 if exito else 500

@app.route('/api/eliminar-directo', methods=['POST'])
def eliminar_directo():
    data = request.get_json()
    id_equipo = data.get('idEquipo')
    tipo = data.get('tipo')  # 'usuario' o 'grupo'
    nombre = data.get('nombre')

    if not id_equipo or not tipo or not nombre:
        return jsonify({'mensaje': 'Faltan datos'}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT ip, puerto, usuario, contrasena FROM equipos WHERE id = %s", (id_equipo,))
    equipo = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not equipo:
        return jsonify({'mensaje': 'Equipo no encontrado'}), 404

    if tipo == "usuario":
        exito, mensaje = eliminar_usuario(equipo['ip'], equipo['puerto'], equipo['usuario'], equipo['contrasena'], nombre)
    elif tipo == "grupo":
        exito, mensaje = eliminar_grupo(equipo['ip'], equipo['puerto'], equipo['usuario'], equipo['contrasena'], nombre)
    else:
        return jsonify({'mensaje': 'Tipo inválido'}), 400

    return jsonify({'mensaje': mensaje}), 200 if exito else 500


@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'estado': 'activo'}), 200

if __name__ == '__main__':
    app.run(debug=True)
