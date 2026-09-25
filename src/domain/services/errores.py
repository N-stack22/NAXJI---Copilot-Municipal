class ErrorDominio(Exception):
    """Error esperado y seguro para mostrar al cliente."""


class DatosInvalidos(ErrorDominio):
    pass


class NoAutorizado(ErrorDominio):
    pass


class NoEncontrado(ErrorDominio):
    pass


class ConflictoEstado(ErrorDominio):
    pass


class ErrorGeneracion(ErrorDominio):
    pass
