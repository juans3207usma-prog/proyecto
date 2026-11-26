// Unico punto que habla HTTP: URL base y manejo de errores.
const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function pedir(ruta, opciones = {}) {
  const res = await fetch(`${API}${ruta}`, {
    headers: { "Content-Type": "application/json" },
    ...opciones,
  });
  const datos = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detalle = Array.isArray(datos.detail)
      ? datos.detail.map((d) => d.msg).join(", ")
      : datos.detail;
    throw new Error(detalle ?? "Error en la solicitud");
  }
  return datos;
}

export const enviar = (ruta, cuerpo) =>
  pedir(ruta, { method: "POST", body: JSON.stringify(cuerpo) });
