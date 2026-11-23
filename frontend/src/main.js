import "./style.css";
import {
  getAlertasStockBajo,
  getPorVencer,
  getProductos,
  registrarEntrada,
  registrarSalida,
} from "./api.js";

const $ = (selector) => document.querySelector(selector);

function mostrarMensaje(texto, esError = false) {
  const el = $("#mensaje");
  el.textContent = texto;
  el.className = esError ? "error" : "ok";
}

// Se usa textContent (nunca innerHTML) para no inyectar HTML desde los datos.
function celda(texto) {
  const td = document.createElement("td");
  td.textContent = texto;
  return td;
}

function pintarProductos(productos) {
  const tbody = $("#tabla-productos");
  tbody.replaceChildren(
    ...productos.map((p) => {
      const fila = document.createElement("tr");
      if (p.stock < p.stock_minimo) fila.className = "bajo";
      fila.append(celda(p.nombre), celda(`$${p.precio}`), celda(p.stock), celda(p.stock_minimo));
      return fila;
    }),
  );

  for (const select of document.querySelectorAll("select[name=producto_id]")) {
    select.replaceChildren(
      ...productos.map((p) => {
        const opcion = document.createElement("option");
        opcion.value = p.id;
        opcion.textContent = p.nombre;
        return opcion;
      }),
    );
  }
}

function pintarLista(selector, items, formato, vacio) {
  const lista = $(selector);
  if (items.length === 0) {
    const li = document.createElement("li");
    li.textContent = vacio;
    lista.replaceChildren(li);
    return;
  }
  lista.replaceChildren(
    ...items.map((item) => {
      const li = document.createElement("li");
      li.textContent = formato(item);
      return li;
    }),
  );
}

export async function recargar() {
  const [productos, bajos, porVencer] = await Promise.all([
    getProductos(),
    getAlertasStockBajo(),
    getPorVencer(),
  ]);
  pintarProductos(productos);
  $("#badge").textContent = bajos.length;
  $(".alerta-badge").classList.toggle("activa", bajos.length > 0);
  pintarLista(
    "#lista-alertas",
    bajos,
    (a) => `${a.nombre}: ${a.stock} unidades (minimo ${a.stock_minimo})`,
    "Sin alertas de stock bajo",
  );
  pintarLista(
    "#lista-vencer",
    porVencer,
    (l) => `${l.producto} - lote ${l.numero_lote}: ${l.cantidad} u. vencen el ${l.fecha_vencimiento}`,
    "Nada por vencer",
  );
}

function manejarFormulario(selector, accion, mensajeOk) {
  $(selector).addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const form = evento.target;
    const datos = Object.fromEntries(new FormData(form));
    datos.producto_id = Number(datos.producto_id);
    datos.cantidad = Number(datos.cantidad);
    try {
      await accion(datos);
      mostrarMensaje(mensajeOk);
      form.reset();
      await recargar();
    } catch (error) {
      mostrarMensaje(error.message, true);
    }
  });
}

manejarFormulario("#form-entrada", registrarEntrada, "Entrada registrada");
manejarFormulario("#form-salida", registrarSalida, "Salida registrada");

recargar().catch(() => mostrarMensaje("No se pudo conectar con la API", true));
