import { pedir } from "./cliente.js";

export const getStockBajo = () => pedir("/alertas/stock-bajo");
export const getPorVencer = (dias = 30) => pedir(`/alertas/por-vencer?dias=${dias}`);
