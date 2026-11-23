class ErrorNegocio(Exception):
    """Error de regla de negocio; `status` es el codigo HTTP asociado."""

    status = 400


class NoEncontrado(ErrorNegocio):
    status = 404


class Conflicto(ErrorNegocio):
    status = 409


class StockInsuficiente(ErrorNegocio):
    status = 409
