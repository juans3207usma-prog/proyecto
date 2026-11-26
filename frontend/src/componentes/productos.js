import { $, crear } from "./dom.js";

export function pintarTabla(productos) {
  $("#tabla-productos").replaceChildren(
    ...productos.map((p) => {
      const fila = crear("tr");
      if (p.stock < p.stock_minimo) fila.className = "bajo";
      fila.append(
        crear("td", p.nombre),
        crear("td", `$${p.precio}`),
        crear("td", p.stock),
        crear("td", p.stock_minimo),
      );
      return fila;
    }),
  );
}

export function pintarSelectores(productos) {
  for (const select of document.querySelectorAll("select[name=producto_id]")) {
    select.replaceChildren(
      ...productos.map((p) => {
        const opcion = crear("option", p.nombre);
        opcion.value = p.id;
        return opcion;
      }),
    );
  }
}
