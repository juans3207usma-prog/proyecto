import { $, crear } from "./dom.js";

function pintarLista(selector, items, formato, vacio) {
  const textos = items.length > 0 ? items.map(formato) : [vacio];
  $(selector).replaceChildren(...textos.map((texto) => crear("li", texto)));
}

export function pintarStockBajo(alertas) {
  $("#badge").textContent = alertas.length;
  $(".alerta-badge").classList.toggle("activa", alertas.length > 0);
  pintarLista(
    "#lista-alertas",
    alertas,
    (a) => `${a.nombre}: ${a.stock} unidades (minimo ${a.stock_minimo})`,
    "Sin alertas de stock bajo",
  );
}

export function pintarPorVencer(lotes) {
  pintarLista(
    "#lista-vencer",
    lotes,
    (l) => `${l.producto} - lote ${l.numero_lote}: ${l.cantidad} u. vencen el ${l.fecha_vencimiento}`,
    "Nada por vencer",
  );
}
