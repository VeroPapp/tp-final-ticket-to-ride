const $ = id => document.getElementById(id);
let DATA = { usuarios: [], todos_los_usuarios: [], representantes: [], categorias: [], productos: [], tickets: [], user_rol: "" };

try {
    const el = $('server-data');
    if (el) DATA = JSON.parse(el.textContent);
} catch (e) { console.error("Error al parsear DATA:", e); }

// ==========================================
// UTILIDADES CENTRALIZADAS
// ==========================================
async function apiCall(url, method = "GET", body = null) {
    const opts = { method, headers: { "Content-Type": "application/json" } };
    if (body) opts.body = JSON.stringify(body);
    
    const resp = await fetch(url, opts);
    const json = await resp.json();
    if (!resp.ok || !json.ok) throw new Error(json.message || "Error desconocido");
    return json;
}

function toast(msg, type = "success") {
    const color = type === "error" ? "danger" : "success";
    const id = "toast-" + Date.now();
    $("toast-container").insertAdjacentHTML("beforeend", `
        <div id="${id}" class="toast align-items-center text-bg-${color} border-0">
            <div class="d-flex">
                <div class="toast-body">${msg}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>`);
    const el = $(id);
    new bootstrap.Toast(el, { delay: 3500 }).show();
    el.addEventListener("hidden.bs.toast", () => el.remove());
}

function confirmar(mensaje) {
    const modalEl = $("modalConfirmar");
    if (!modalEl) return Promise.resolve(window.confirm(mensaje));
    
    $("conf-mensaje").textContent = mensaje;
    const modal = new bootstrap.Modal(modalEl);
    return new Promise(resolve => {
        $("conf-ok").onclick = () => { modal.hide(); resolve(true); };
        $("conf-cancel").onclick = () => { modal.hide(); resolve(false); };
        modal.show();
    });
}

function showModal(id, reset = false) {
    if (reset) document.querySelector(`#${id} form`)?.reset();
    new bootstrap.Modal($(id)).show();
}

async function submitData(url, data, successMsg, modalToHide = null) {
    try {
        await apiCall(url, "POST", data);
        toast(successMsg);
        if (modalToHide) bootstrap.Modal.getInstance($(modalToHide)).hide();
        setTimeout(() => location.reload(), 500);
    } catch (err) { toast(err.message, "error"); }
}

async function deleteItem(url, confirmMsg) {
    if (!(await confirmar(confirmMsg))) return;
    try {
        await apiCall(url, "POST");
        toast("Eliminado correctamente");
        setTimeout(() => location.reload(), 500);
    } catch (err) { toast(err.message, "error"); }
}

// ==========================================
// USUARIOS
// ==========================================
const abrirCrearUsuario = () => showModal("modalCrearUsuario", true);
const guardarUsuario = e => {
    e.preventDefault();
    const f = e.target;
    submitData("/usuarios/crear", { nombre: f.nombre.value, mail: f.mail.value, psw: f.psw.value, rol: f.rol.value }, "Usuario creado");
};

const abrirEditarUsuario = btn => {
    const u = DATA.usuarios.find(x => x.id === parseInt(btn.dataset.id));
    if (u) {
        const f = document.querySelector("#modalEditarUsuario form");
        f.id.value = u.id; f.nombre.value = u.nombre; f.mail.value = u.mail;
        showModal("modalEditarUsuario");
    }
};

const actualizarUsuario = e => {
    e.preventDefault();
    const f = e.target;
    submitData(`/usuarios/${f.id.value}/actualizar`, { nombre: f.nombre.value, mail: f.mail.value }, "Usuario actualizado");
};

const eliminarUsuario = btn => {
    const u = DATA.usuarios.find(x => x.id === parseInt(btn.dataset.id));
    deleteItem(`/usuarios/${btn.dataset.id}/eliminar`, `¿Eliminar al usuario "${u ? u.nombre : btn.dataset.id}"?`);
};

// ==========================================
// CATEGORÍAS
// ==========================================
const abrirCrearCategoria = () => showModal("modalCrearCategoria", true);
const guardarCategoria = e => {
    e.preventDefault();
    submitData("/categorias/crear", { nombre: e.target.nombre.value }, "Categoría creada");
};
const eliminarCategoria = btn => {
    const c = DATA.categorias.find(x => x.id === parseInt(btn.dataset.id));
    deleteItem(`/categorias/${btn.dataset.id}/eliminar`, `¿Eliminar la categoría "${c ? c.nombre : btn.dataset.id}"?`);
};

// ==========================================
// PRODUCTOS
// ==========================================
const abrirCrearProducto = () => {
    if (DATA.categorias.length === 0) return toast("Creá una categoría primero", "error");
    showModal("modalCrearProducto", true);
};

const guardarProducto = e => {
    e.preventDefault();
    const f = e.target;
    submitData("/productos/crear", {
        nombre: f.nombre.value, marca: f.marca.value, modelo: f.modelo.value, codigo: f.codigo.value, categoria_id: parseInt(f.categoria_id.value)
    }, "Producto creado");
};

const abrirEditarProducto = btn => {
    const p = DATA.productos.find(x => x.id === parseInt(btn.dataset.id));
    if (p) {
        const f = document.querySelector("#modalEditarProducto form");
        f.id.value = p.id; f.nombre.value = p.nombre; f.categoria_id.value = p.categoria_id || "";
        showModal("modalEditarProducto");
    }
};

const actualizarProducto = e => {
    e.preventDefault();
    const f = e.target;
    submitData(`/productos/${f.id.value}/actualizar`, {
        nombre: f.nombre.value, categoria_id: f.categoria_id.value ? parseInt(f.categoria_id.value) : null
    }, "Producto actualizado");
};

const eliminarProducto = btn => {
    const p = DATA.productos.find(x => x.id === parseInt(btn.dataset.id));
    deleteItem(`/productos/${btn.dataset.id}/eliminar`, `¿Eliminar el producto "${p ? p.nombre : btn.dataset.id}"?`);
};

// ==========================================
// TICKETS
// ==========================================
const abrirCrearTicket = () => {
    if (DATA.productos.length === 0) return toast("Creá un producto primero", "error");
    showModal("modalCrearTicket", true);
};

const guardarTicket = e => {
    e.preventDefault();
    const f = e.target;
    submitData("/tickets/crear", {
        cliente_id: f.cliente_id ? parseInt(f.cliente_id.value) : null,
        producto_id: parseInt(f.producto_id.value),
        representante_id: f.representante_id && f.representante_id.value ? parseInt(f.representante_id.value) : null,
        descripcion: f.descripcion.value,
        prioridad: f.prioridad ? f.prioridad.value : "Media"
    }, "Ticket creado");
};

async function abrirGestionar(btn) {
    const tid = parseInt(btn.dataset.id);
    try {
        const data = await apiCall(`/tickets/${tid}/detalle`);
        const t = data.ticket;
        
        // Cabecera
        $("gt-id").textContent = t.id; $("gt-desc").textContent = t.descripcion;
        $("gt-estado").textContent = t.estado; $("gt-prio").textContent = t.prioridad;
        $("gt-cliente").textContent = t.cliente_id; $("gt-rep").textContent = t.representante_id || "-";
        $("gt-prod").textContent = t.producto_id || "-";

        // Inputs ocultos
        ["gt-update-id", "gt-msg-id"].forEach(id => { if ($(id)) $(id).value = t.id; });

        const esCliente = DATA.user_rol === 'Cliente';
        const esAdmin = DATA.user_rol === 'Administrador';
        const cerrado = t.estado === "Cerrado";

        const estadoSelect = $("gt-estado-select");
        if (estadoSelect) estadoSelect.value = t.estado;

        // Botones de acción
        let botones = "";
        if (!esCliente) {
            botones += cerrado 
                ? `<button class="btn btn-warning" onclick="reabrirTicket(${t.id})"><i class="bi bi-unlock"></i> Reabrir Ticket</button> `
                : `<button class="btn btn-success" onclick="cerrarTicket(${t.id})"><i class="bi bi-lock"></i> Cerrar Ticket</button> `;
        }
        if (esAdmin) botones += `<button class="btn btn-outline-danger" onclick="eliminarTicket(${t.id})"><i class="bi bi-trash"></i> Eliminar</button>`;
        $("gt-acciones").innerHTML = botones;

        // Visibilidad de formularios
        const cardAct = $("gt-card-actualizar");
        const cardMsg = $("gt-card-mensaje");
        if (cerrado) {
            if (cardAct) cardAct.style.display = "none";
            if (cardMsg) cardMsg.style.display = "none";
        } else {
            if (cardAct) cardAct.style.display = esCliente ? "none" : "";
            if (cardMsg) cardMsg.style.display = "";
            
            // Select de remitentes (solo Admin)
            const select = $("gt-msg-remitente");
            if (select && select.tagName === "SELECT") {
                select.innerHTML = '<option value="">Elegir...</option>';
                [t.cliente_id, t.representante_id].filter(x => x).forEach(uid => {
                    const u = DATA.todos_los_usuarios.find(x => x.id === uid);
                    if (u) select.insertAdjacentHTML("beforeend", `<option value="${u.id}">${u.nombre} (${u.rol})</option>`);
                });
            }
        }

        // Historial
        const { hitos, mensajes } = data.historial;
        $("gt-hitos").innerHTML = hitos.length ? hitos.map(h => `
            <li class="list-group-item"><small class="text-muted">${h.fecha}</small><br>${h.descripcion}</li>
        `).join("") : '<li class="list-group-item text-muted">Sin hitos</li>';
        
        $("gt-mensajes").innerHTML = mensajes.length ? mensajes.map(m => `
            <li class="list-group-item"><strong>${m.remitente}:</strong> ${m.contenido}<br><small class="text-muted">${m.fecha}</small></li>
        `).join("") : '<li class="list-group-item text-muted">Sin mensajes</li>';

        showModal("modalGestionar");
    } catch (err) { toast(err.message, "error"); }
}

const enviarMensaje = e => {
    e.preventDefault();
    const remitente = $("gt-msg-remitente");
    submitData(`/tickets/${$("gt-msg-id").value}/mensaje`, {
        remitente_id: remitente ? parseInt(remitente.value) : null,
        contenido: $("gt-msg-contenido").value
    }, "Mensaje enviado", "modalGestionar");
};

const actualizarTicket = e => {
    e.preventDefault();
    const rep = $("gt-update-rep");
    submitData(`/tickets/${$("gt-update-id").value}/actualizar`, {
        descripcion: $("gt-update-desc").value || null,
        prioridad: $("gt-update-prio").value || null,
        representante_id: rep && rep.value ? parseInt(rep.value) : null
    }, "Ticket actualizado", "modalGestionar");
};

const cambiarEstado = () => {
    const tid = $("gt-id").textContent;
    const nuevoEstado = $("gt-estado-select").value;
    submitData(`/tickets/${tid}/estado`, { nuevo_estado: nuevoEstado }, "Estado actualizado", "modalGestionar");
};

const cerrarTicket = tid => deleteItem(`/tickets/${tid}/cerrar`, "¿Cerrar este ticket?");
const reabrirTicket = tid => deleteItem(`/tickets/${tid}/reabrir`, "¿Reabrir este ticket?");
const eliminarTicket = tid => deleteItem(`/tickets/${tid}/eliminar`, `¿Eliminar el ticket #${tid}?`);

// ==========================================
// NOTIFICACIONES
// ==========================================
const marcarLeida = btn => submitData(`/notificaciones/${btn.dataset.id}/leer`, {}, "Notificación leída");
const eliminarNotif = btn => deleteItem(`/notificaciones/${btn.dataset.id}/eliminar`, "¿Eliminar esta notificación?");