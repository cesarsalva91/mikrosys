import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='WUppa2-.',
        database='mikrotik_config'
    )
