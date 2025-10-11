from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Cliente, Usuario, HistorialCliente
from .forms import ClienteForm, RegistroForm
from django.db.models import Q


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
# Crear usuario (solo admin/superadmin) sin cambiar sesión actual
# -----------------------------
@login_required
def crear_usuario(request):
    if not (request.user.is_superuser or request.user.rol in ['admin', 'superadmin']):
        messages.error(request, "🚫 No tienes permiso para crear usuarios.")
        return redirect('lista_clientes')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            # No autenticar ni cambiar la sesión; solo crear el usuario
            nuevo_usuario = form.save(commit=False)
            # El formulario ya asigna rol 'usuario' por defecto
            nuevo_usuario.save()
            messages.success(request, f"✅ Usuario '{nuevo_usuario.username}' creado correctamente.")
            return redirect('lista_clientes')
        else:
            messages.error(request, "❌ Revisa los errores del formulario.")
    else:
        form = RegistroForm()

    return render(request, 'clientes/crear_usuario.html', { 'form': form })


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
# Listar clientes activos con búsqueda y paginación (más recientes primero)
# -----------------------------
@login_required
def lista_clientes(request):
    query = request.GET.get('q', '').strip()  # Limpia espacios

    # Base: clientes activos, los más recientes primero
    clientes_list = Cliente.objects.filter(activo=True).order_by('-creado_en')

    if query:
        # Filtra sin distinguir mayúsculas/minúsculas
        clientes_list = clientes_list.filter(
            Q(nombre__icontains=query) |
            Q(compania__icontains=query) |
            Q(identificacion__icontains=query)
        )

        # Ordena coincidencias: exactas primero, luego parciales
        query_lower = query.lower()
        clientes_list = sorted(
            clientes_list,
            key=lambda c: (
                0 if c.nombre.lower().startswith(query_lower) else
                1 if query_lower in c.nombre.lower() else
                2
            )
        )

    # Paginación
    paginator = Paginator(clientes_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'clientes/lista.html', {
        'page_obj': page_obj,
        'query': query
    })


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
# Ver detalles del cliente y edición
# -----------------------------
@login_required
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    # Determinar si el usuario puede editar
    puede_editar = request.user.rol in ['admin', 'superadmin'] or request.user.is_superuser

    if request.method == "POST" and puede_editar:
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.save(usuario=request.user)  # Historial automático
            messages.success(request, "✅ Cliente actualizado correctamente.")
            return redirect('detalle_cliente', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)

    # Preparar URL de Google Maps de forma segura (puede ser None)
    maps_url = cliente.google_maps_link

    return render(request, 'clientes/detalle.html', {
        'cliente': cliente,
        'form': form,
        'maps_url': maps_url,
        'historial': cliente.historial.all().order_by('-fecha_edicion'),
        'puede_editar': puede_editar
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
# Listar clientes eliminados con paginación
# -----------------------------
@login_required
@rol_requerido(['admin', 'superadmin'])
def clientes_eliminados(request):
    clientes_list = Cliente.objects.filter(activo=False).order_by('-fecha_eliminacion')
    paginator = Paginator(clientes_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'clientes/eliminados.html', {'clientes': page_obj})


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
