from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps
from django.utils import timezone
from .models import Cliente, Usuario, HistorialCliente
from .forms import ClienteForm, RegistroForm
from django.db.models.fields.files import FieldFile



# -----------------------------
# Registro de usuarios
# -----------------------------
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = 'usuario'  # Rol por defecto
            user.save()
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
    """
    Restringe el acceso a usuarios cuyo rol no esté en la lista de roles permitidos.
    Si no cumple, muestra un mensaje y redirige a la lista de clientes.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and (request.user.rol in roles or request.user.is_superuser):
                return view_func(request, *args, **kwargs)
            messages.error(request, "🚫 No tienes permiso para acceder a esta página.")
            return redirect('lista_clientes')
        return _wrapped_view
    return decorator


# -----------------------------
# Listar clientes activos
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
    direccion_url = cliente.direccion or cliente.pais
    maps_url = f"https://www.google.com/maps/search/?api=1&query={direccion_url.replace(' ', '+')}"
    return render(request, 'clientes/detalle.html', {
        'cliente': cliente,
        'maps_url': maps_url
    })


# -----------------------------
# Eliminar (ocultar) cliente
# -----------------------------
@login_required
@rol_requerido(['admin', 'superadmin'])
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.activo = False
    cliente.fecha_eliminacion = timezone.now()
    cliente.save()
    messages.warning(request, "🗑️ Cliente marcado para eliminación (se eliminará definitivamente en 30 días).")
    return redirect('lista_clientes')


# -----------------------------
# Listar clientes eliminados
# -----------------------------
@login_required
@rol_requerido(['admin', 'superadmin'])
def clientes_eliminados(request):
    clientes = Cliente.objects.filter(activo=False)
    return render(request, 'clientes/eliminados.html', {'clientes': clientes})


# -----------------------------
# Restaurar cliente eliminado
# -----------------------------
@login_required
@rol_requerido(['admin', 'superadmin'])
def restaurar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.activo = True
    cliente.fecha_eliminacion = None
    cliente.save()
    messages.success(request, f"✅ El cliente '{cliente.nombre}' fue restaurado correctamente.")
    return redirect('clientes_eliminados')

# -----------------------------
# detalle_cliente
# -----------------------------
@login_required
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    # Definir si el usuario puede editar
    puede_editar = request.user.rol in ['admin', 'superadmin'] or request.user.is_superuser

    if request.method == "POST" and puede_editar:
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            # Guardar cambios pasando el usuario que hace la edición
            cliente = form.save(commit=False)
            cliente.save(usuario=request.user)  # 👈 historial automático
            messages.success(request, "✅ Cliente actualizado correctamente.")
            return redirect('detalle_cliente', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/detalle.html', {
        'cliente': cliente,
        'form': form,
        'maps_url': cliente.google_maps_link,
        'historial': cliente.historial.all().order_by('-fecha_edicion'),
        'puede_editar': puede_editar
    })