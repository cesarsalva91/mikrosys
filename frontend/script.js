function cargarEquipos() {
  fetch('http://localhost:5000/api/equipos')
    .then(res => res.json())
    .then(equipos => {
      const select = document.getElementById('equipoSelect');
      select.innerHTML = '';
      equipos.forEach(eq => {
        const option = document.createElement('option');
        option.value = eq.id;
        option.textContent = `${eq.nombre} (${eq.ip}:${eq.puerto})`;
        select.appendChild(option);
      });
    })
    .catch(err => console.error('Error al cargar equipos:', err));
}

function mostrarAcciones() {
  fetch('http://localhost:5000/api/acciones')
    .then(res => res.json())
    .then(data => {
      const lista = document.getElementById('listaAcciones');
      lista.innerHTML = '';
      data.acciones.forEach(accion => {
        const li = document.createElement('li');
        li.textContent = accion;
        lista.appendChild(li);
      });
    })
    .catch(error => console.error('Error al obtener acciones:', error));
}

// Mostrar modales según acción seleccionada
document.getElementById('listaAcciones').addEventListener('click', function (e) {
  const texto = e.target.textContent;
  if (texto.startsWith("1")) {
    document.getElementById('modalGrupo').style.display = 'block';
  }
  if (texto.startsWith("2")) {
    document.getElementById('modal').style.display = 'block';
  }
  if (texto.startsWith("6")) {
    document.getElementById('modalRomon').style.display = 'block';
  }
});

document.getElementById('cerrarModal').addEventListener('click', function () {
  document.getElementById('modal').style.display = 'none';
});
document.getElementById('cerrarModalRomon').addEventListener('click', function () {
  document.getElementById('modalRomon').style.display = 'none';
});
document.getElementById('cerrarModalGrupo').addEventListener('click', function () {
  document.getElementById('modalGrupo').style.display = 'none';
});

// Crear usuario
document.getElementById('formCrearUsuario').addEventListener('submit', function (e) {
  e.preventDefault();

  const idEquipo = document.getElementById('equipoSelect').value;
  const nombre = document.getElementById('nuevoUsuario').value;
  const clave = document.getElementById('claveUsuario').value;
  const grupo = document.getElementById('grupoUsuario').value;

  fetch('http://localhost:5000/api/crear-usuario', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idEquipo, nombre, clave, grupo })
  })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      const resultado = document.getElementById('resultadoCreacion');
      resultado.textContent = body.mensaje;
      resultado.style.color = status === 200 ? 'lightgreen' : 'salmon';
    })
    .catch(err => {
      document.getElementById('resultadoCreacion').textContent = 'Error al crear el usuario.';
      console.error(err);
    });
});

// Activar / Desactivar ROMON
function modificarRomon(habilitar) {
  const idEquipo = document.getElementById('equipoSelect').value;

  fetch('http://localhost:5000/api/romon', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idEquipo, habilitar })
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById('resultadoRomon').textContent = data.mensaje;
    })
    .catch(err => {
      document.getElementById('resultadoRomon').textContent = 'Error al modificar ROMON.';
      console.error(err);
    });
}

// Mostrar nombre de skin automáticamente al seleccionar archivo
document.getElementById('archivoSkin').addEventListener('change', function () {
  const archivo = this.files[0];
  const textoSkin = document.getElementById('skinNombreAuto');

  if (archivo) {
    const nombre = archivo.name;
    const sinExtension = nombre.substring(0, nombre.lastIndexOf('.'));
    textoSkin.textContent = `Nombre del skin: ${sinExtension}`;
  } else {
    textoSkin.textContent = 'Nombre del skin: (se definirá según el archivo seleccionado)';
  }
});

// Crear grupo (con posible subida de skin)
document.getElementById('formCrearGrupo').addEventListener('submit', function (e) {
  e.preventDefault();

  const idEquipo = document.getElementById('equipoSelect').value;
  const nombre = document.getElementById('nombreGrupo').value;
  const checkboxes = document.querySelectorAll('#politicasContainer input[type="checkbox"]:checked');
  const politicas = Array.from(checkboxes).map(cb => cb.value).join(',');
  const archivoSkin = document.getElementById('archivoSkin').files[0];
  const resultado = document.getElementById('resultadoGrupo');

  // Determinar nombre del skin
  let skin = '';
  if (archivoSkin) {
    const nombreArchivo = archivoSkin.name;
    skin = nombreArchivo.substring(0, nombreArchivo.lastIndexOf('.'));
  }

  if (!nombre || politicas.length === 0) {
    resultado.textContent = 'Debe completar nombre y seleccionar al menos una política.';
    resultado.style.color = 'salmon';
    return;
  }

  if (archivoSkin && skin) {
    const formData = new FormData();
    formData.append('idEquipo', idEquipo);
    formData.append('nombreSkin', skin);
    formData.append('archivoSkin', archivoSkin);

    fetch('http://localhost:5000/api/subir-skin', {
      method: 'POST',
      body: formData
    })
      .then(res => res.json().then(data => ({ status: res.status, body: data })))
      .then(({ status, body }) => {
        if (status !== 200) {
          resultado.textContent = 'Error al subir skin: ' + body.mensaje;
          resultado.style.color = 'salmon';
          return;
        }
        crearGrupo(idEquipo, nombre, politicas, skin, resultado);
      })
      .catch(err => {
        resultado.textContent = 'Error al subir el skin.';
        resultado.style.color = 'salmon';
        console.error(err);
      });
  } else {
    crearGrupo(idEquipo, nombre, politicas, skin, resultado);
  }
});

function crearGrupo(idEquipo, nombre, politicas, skin, resultado) {
  fetch('http://localhost:5000/api/crear-grupo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idEquipo, nombre, politicas, skin })
  })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      resultado.textContent = body.mensaje;
      resultado.style.color = status === 200 ? 'lightgreen' : 'salmon';
    })
    .catch(err => {
      resultado.textContent = 'Error al crear grupo.';
      resultado.style.color = 'salmon';
      console.error(err);
    });
}

// Cargar todo al iniciar
cargarEquipos();
mostrarAcciones();
