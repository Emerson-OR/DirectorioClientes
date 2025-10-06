from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Cliente, Usuario
from .forms import ClienteForm, RegistroForm
from django.http import HttpResponseForbidden

# Registro de usuarios
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_clientes')
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})

# Login y logout usarían tus vistas genéricas actuales

# Decorador para roles
def rol_requerido(roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.rol in roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder a esta página")
        return _wrapped_view
    return decorator

# Vistas de clientes
@login_required
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista.html', {'clientes': clientes})

@login_required
@rol_requerido(['admin', 'superadmin'])
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.creado_por = request.user
            cliente.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'clientes/agregar.html', {'form': form})

@login_required
@rol_requerido(['admin', 'superadmin'])
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.delete()
    return redirect('lista_clientes')
