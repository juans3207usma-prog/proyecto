// Punto de entrada: solo conecta la capa de API con los componentes.
import "./estilos/style.css";
import { getPorVencer, getStockBajo } from "./api/alertas.js";
import { registrarEntrada, registrarSalida } from "./api/movimientos.js";
import { getProductos } from "./api/productos.js";
import { pintarPorVencer, pintarStockBajo } from "./componentes/alertas.js";
import { conectarFormulario } from "./componentes/formularios.js";
import { mostrarMensaje } from "./componentes/mensaje.js";
import { pintarSelectores, pintarTabla } from "./componentes/productos.js";

async function recargar() {
  const [productos, stockBajo, porVencer] = await Promise.all([
    getProductos(),
    getStockBajo(),
    getPorVencer(),
  ]);
  pintarTabla(productos);
  pintarSelectores(productos);
  pintarStockBajo(stockBajo);
  pintarPorVencer(porVencer);
}

conectarFormulario("#form-entrada", registrarEntrada, "Entrada registrada", recargar);
conectarFormulario("#form-salida", registrarSalida, "Salida registrada", recargar);

recargar().catch(() => mostrarMensaje("No se pudo conectar con la API", true));
