from django.shortcuts import redirect
from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware

class CustomCsrfMiddleware(CsrfViewMiddleware):
    def _reject(self, request, reason):
        # Redirige al login si el token CSRF es inválido
        if reason and '/accounts/login/' not in request.path:
            return redirect(settings.LOGIN_URL)
        return super()._reject(request, reason)
