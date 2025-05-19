import os
import zipfile
import tempfile
import paramiko

def subir_skin_a_router(ip, puerto_ssh, usuario, clave, archivo_skin, nombre_skin):
    try:
        extension = os.path.splitext(archivo_skin)[1].lower()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=ip,
            username=usuario,
            password=clave,
            port=puerto_ssh,
            look_for_keys=False,     # 🔐 importante
            allow_agent=False        # 🔐 importante
        )

        sftp = ssh.open_sftp()
        remote_path = "/skins/"

        try:
            sftp.mkdir(remote_path)
        except IOError:
            pass  # Ya existe

        if extension == '.zip':
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(archivo_skin, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                for archivo in os.listdir(temp_dir):
                    local_file = os.path.join(temp_dir, archivo)
                    remote_file = remote_path + archivo
                    sftp.put(local_file, remote_file)

        elif extension == '.json':
            sftp.put(archivo_skin, remote_path + os.path.basename(archivo_skin))

        else:
            return False, 'Error al subir skin: formato no compatible (solo .zip o .json)'

        sftp.close()
        ssh.close()
        return True, f'Skin \"{nombre_skin}\" subido correctamente'

    except Exception as e:
        return False, f'Error al subir skin: {str(e)}'
