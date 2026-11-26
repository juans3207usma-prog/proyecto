import { enviar } from "./cliente.js";

export const registrarEntrada = (datos) => enviar("/movimientos/entrada", datos);
export const registrarSalida = (datos) => enviar("/movimientos/salida", datos);
