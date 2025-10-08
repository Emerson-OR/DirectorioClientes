from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Cliente, Usuario
from .forms import ClienteForm, RegistroForm
from django.http import HttpResponseForbidden
from django.contrib import messages

# -----------------------------
# Registro de usuarios
# -----------------------------
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=user.username, password=request.POST['password1'])
            if user:
                login(request, user)
                return redirect('lista_clientes')
        else:
            print("❌ Errores del formulario:", form.errors)
    else:
        form = RegistroForm()

    return render(request, 'registration/registro.html', {'form': form})


# -----------------------------
# Decorador de roles
# -----------------------------
def rol_requerido(roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.rol in roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder a esta página")
        return _wrapped_view
    return decorator


# -----------------------------
# Listar clientes
# -----------------------------
@login_required
def lista_clientes(request):
    clientes = Cliente.objects.filter(activo=True)
    return render(request, 'clientes/lista.html', {'clientes': clientes})



# -----------------------------
# Agregar cliente
# -----------------------------
@login_required
@rol_requerido(['admin', 'superadmin'])
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.creado_por = request.user
            cliente.save()
            messages.success(request, "✅ Cliente agregado exitosamente.")
            return redirect('lista_clientes')
        else:
            messages.error(request, "❌ Ocurrió un error al agregar el cliente.")
    else:
        form = ClienteForm()

    return render(request, 'clientes/agregar.html', {'form': form})


# -----------------------------
# Ver detalles del cliente
# -----------------------------
@login_required
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    # Genera enlace directo a Google Maps usando la dirección o el país
    direccion_url = cliente.direccion or cliente.pais
    maps_url = f"https://www.google.com/maps/search/?api=1&query={direccion_url.replace(' ', '+')}"
    
    return render(request, 'clientes/detalle.html', {
        'cliente': cliente,
        'maps_url': maps_url
    })


# -----------------------------
# Eliminar cliente
# -----------------------------
@login_required
@rol_requerido(['admin', 'superadmin'])
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.activo = False  # 🔹 Se oculta en lugar de eliminar
    cliente.save()
    messages.warning(request, "🗑️ Cliente oculto correctamente.")
    return redirect('lista_clientes')

