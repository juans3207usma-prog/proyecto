import { $ } from "./dom.js";
import { mostrarMensaje } from "./mensaje.js";

export function conectarFormulario(selector, accion, mensajeOk, alTerminar) {
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
      await alTerminar();
    } catch (error) {
      mostrarMensaje(error.message, true);
    }
  });
}
