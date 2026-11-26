import { $ } from "./dom.js";

export function mostrarMensaje(texto, esError = false) {
  const el = $("#mensaje");
  el.textContent = texto;
  el.className = esError ? "error" : "ok";
}
