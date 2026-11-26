export const $ = (selector) => document.querySelector(selector);

// Se usa textContent (nunca innerHTML) para no inyectar HTML desde los datos.
export function crear(etiqueta, texto) {
  const elemento = document.createElement(etiqueta);
  if (texto !== undefined) elemento.textContent = texto;
  return elemento;
}
