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
  if (texto.startsWith("3")) {
  document.getElementById('modalEliminarDirecto').style.display = 'block';
  }
  if (texto.startsWith("4")) {
  document.getElementById('modalNTP').style.display = 'block';
  }
  if (texto.startsWith("5")) {
  document.getElementById('modalSNMP').style.display = 'block';
  }
  if (texto.startsWith("6")) {
    document.getElementById('modalRomon').style.display = 'block';
  }
});

document.getElementById('cerrarModalSNMP').addEventListener('click', function () {
  document.getElementById('modalSNMP').style.display = 'none';
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
let romonSecret = null;

function guardarSecretRomon() {
  const secretInput = document.getElementById('romonSecretInput').value.trim();
  const idEquipo = document.getElementById('equipoSelect').value;
  const resultado = document.getElementById('resultadoRomon');

  if (!secretInput) {
    resultado.textContent = 'Debe ingresar una contraseña para el secret.';
    resultado.style.color = 'salmon';
    return;
  }

  if (!idEquipo) {
    resultado.textContent = 'Debe seleccionar un equipo.';
    resultado.style.color = 'salmon';
    return;
  }

  fetch('http://localhost:5000/api/aplicar-secret', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idEquipo, secret: secretInput })
  })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      resultado.textContent = body.mensaje;
      resultado.style.color = status === 200 ? 'lightgreen' : 'salmon';
    })
    .catch(err => {
      resultado.textContent = 'Error al aplicar el secret.';
      resultado.style.color = 'salmon';
      console.error(err);
    });
}



function modificarRomon(habilitar) {
  const idEquipo = document.getElementById('equipoSelect').value;
  const resultado = document.getElementById('resultadoRomon');

  if (!idEquipo) {
    resultado.textContent = 'Debe seleccionar un equipo.';
    resultado.style.color = 'salmon';
    return;
  }

  fetch('http://localhost:5000/api/romon', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idEquipo, habilitar, secret: romonSecret })
  })
  .then(res => res.json().then(data => ({ status: res.status, body: data })))
  .then(({ status, body }) => {
  const resultado = document.getElementById('resultadoRomon');
  resultado.textContent = body.mensaje;
  resultado.style.color = status === 200 ? 'lightgreen' : 'salmon';
  })

  .catch(err => {
    resultado.textContent = 'Error al cambiar estado de ROMON.';
    resultado.style.color = 'salmon';
    console.error(err);
  });
}

function eliminarDirectamente() {
  const idEquipo = document.getElementById('equipoSelect').value;
  const tipo = document.getElementById('tipoEliminacion').value;
  const nombre = document.getElementById('nombreEliminar').value.trim();
  const resultado = document.getElementById('resultadoEliminarDirecto');

  if (!idEquipo || !nombre) {
    resultado.textContent = 'Debe completar todos los campos.';
    resultado.style.color = 'salmon';
    return;
  }

  fetch('http://localhost:5000/api/eliminar-directo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idEquipo, tipo, nombre })
  })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      resultado.textContent = body.mensaje;
      resultado.style.color = status === 200 ? 'lightgreen' : 'salmon';
    })
    .catch(err => {
      resultado.textContent = 'Error al eliminar.';
      resultado.style.color = 'salmon';
      console.error(err);
    });
}

function cerrarModalEliminarDirecto() {
  document.getElementById('modalEliminarDirecto').style.display = 'none';
}

document.getElementById('formModificarNTP').addEventListener('submit', function (e) {
  e.preventDefault();

  const idEquipo = document.getElementById('equipoSelect').value;
  const ntpPrimario = document.getElementById('ntpPrimario').value.trim();
  const ntpSecundario = document.getElementById('ntpSecundario').value.trim();
  const resultado = document.getElementById('resultadoNTP');
  const habilitado = document.getElementById('ntpHabilitado').checked;


  if (!idEquipo || !ntpPrimario) {
    resultado.textContent = 'Debe seleccionar un equipo y completar el NTP primario.';
    resultado.style.color = 'salmon';
    return;
  }

  fetch('http://localhost:5000/api/modificar-ntp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      idEquipo,
      ntpPrimario,
      ntpSecundario: ntpSecundario || null,
      habilitado
    })

  })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      resultado.textContent = body.mensaje;
      resultado.style.color = status === 200 ? 'lightgreen' : 'salmon';
    })
    .catch(err => {
      resultado.textContent = 'Error al modificar NTP.';
      resultado.style.color = 'salmon';
      console.error(err);
    });
});

document.getElementById('cerrarModalNTP').addEventListener('click', function () {
  document.getElementById('modalNTP').style.display = 'none';
});

document.getElementById('formSNMP').addEventListener('submit', function (e) {
  e.preventDefault();

  const idEquipo = document.getElementById('equipoSelect').value;
  const habilitado = document.getElementById('snmpHabilitado').checked;
  const trap_community = document.getElementById('trapCommunity').value.trim();
  const trap_version = document.getElementById('trapVersion').value;
  const trap_generators = document.getElementById('trapGenerators').value;
  const resultado = document.getElementById('resultadoSNMP');

  const nombreComunidad = document.getElementById('nombreComunidad').value.trim();
  const addressesRaw = document.getElementById('addressesComunidad').value.trim();
  const addresses = addressesRaw ? addressesRaw.split(',').map(d => d.trim()) : [];

  if (!idEquipo || !trap_community) {
    resultado.textContent = 'Faltan campos obligatorios.';
    resultado.style.color = 'salmon';
    return;
  }

  const comunidades = [];
  if (nombreComunidad && addresses.length > 0) {
    comunidades.push({
      nombre: nombreComunidad,
      direcciones: addresses
    });
  }

  fetch('http://localhost:5000/api/modificar-snmp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      idEquipo,
      habilitado,
      trap_community,
      trap_version,
      trap_generators,
      comunidades
    })
  })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      resultado.textContent = body.mensaje;
      resultado.style.color = status === 200 ? 'lightgreen' : 'salmon';
    })
    .catch(err => {
      resultado.textContent = 'Error al aplicar configuración SNMP.';
      resultado.style.color = 'salmon';
      console.error(err);
    });
});






// Cargar todo al iniciar
cargarEquipos();
mostrarAcciones();
