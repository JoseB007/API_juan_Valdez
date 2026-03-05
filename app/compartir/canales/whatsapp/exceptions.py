class WhatsappError(Exception):
    """Clase base para errores de WhatsApp."""
    def __init__(self, mensaje, status_code=None, provider_error=None):
        self.mensaje = mensaje
        self.status_code = status_code
        self.provider_error = provider_error
        super().__init__(self.mensaje)

class WhatsappAuthError(WhatsappError):
    """Error de autenticación con el proveedor."""
    pass

class WhatsappValidationError(WhatsappError):
    """Error de validación del mensaje o destinatario."""
    pass

class WhatsappRateLimitError(WhatsappError):
    """Error por exceder los límites de velocidad (Rate Limit)."""
    pass

class WhatsappProviderError(WhatsappError):
    """Error interno del proveedor de servicios."""
    pass
