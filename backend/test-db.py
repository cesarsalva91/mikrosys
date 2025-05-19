from db import obtener_conexion

def testear_conexion():
    try:
        conexion = obtener_conexion()
        if conexion.is_connected():
            print(" Conexión exitosa a la base de datos.")
            print("Base de datos:", conexion.database)
        else:
            print(" No se pudo conectar a la base de datos.")
        conexion.close()
    except Exception as e:
        print(f" Error al conectar: {e}")

if __name__ == '__main__':
    testear_conexion()
