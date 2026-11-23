const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function pedir(ruta, opciones = {}) {
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

export const getProductos = () => pedir("/productos");
export const getAlertasStockBajo = () => pedir("/alertas/stock-bajo");
export const getPorVencer = () => pedir("/alertas/por-vencer?dias=30");

export const registrarEntrada = (datos) =>
  pedir("/movimientos/entrada", { method: "POST", body: JSON.stringify(datos) });

export const registrarSalida = (datos) =>
  pedir("/movimientos/salida", { method: "POST", body: JSON.stringify(datos) });
