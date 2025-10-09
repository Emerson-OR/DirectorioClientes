from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and (user.is_superuser or user.rol in ['admin', 'superadmin']):
            return view_func(request, *args, **kwargs)
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('lista_clientes')
    return wrapper
