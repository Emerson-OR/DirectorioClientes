from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Cliente, Usuario, HistorialCliente, UsuarioCreado
from .forms import ClienteForm, RegistroForm
from django.db.models import Q
from .services.states_api import fetch_us_states


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
            nuevo_usuario = form.save(commit=False)
            nuevo_usuario.save()
            # Registrar quién lo creó
            UsuarioCreado.objects.create(creador=request.user, usuario=nuevo_usuario)
            messages.success(request, f"✅ Usuario '{nuevo_usuario.username}' creado y registrado.")
            return redirect('usuarios_creados')
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
# Listado de usuarios creados por el admin/superadmin actual
# -----------------------------
@login_required
@rol_requerido(['admin', 'superadmin'])
def usuarios_creados(request):
    registros = UsuarioCreado.objects.filter(creador=request.user).select_related('usuario').order_by('-creado_en')
    paginator = Paginator(registros, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'clientes/usuarios_creados.html', { 'registros': page_obj })


# -----------------------------
# Listar clientes activos con búsqueda y paginación (más recientes primero)
# -----------------------------
@login_required
def lista_clientes(request):
    query = request.GET.get('q', '').strip()  # Limpia espacios
    search_field = request.GET.get('field', 'all')

    # Base: clientes activos, los más recientes primero
    clientes_list = Cliente.objects.filter(activo=True).order_by('-creado_en')

    if query:
        # Construir filtro según el campo seleccionado
        if search_field == 'nombre':
            clientes_list = clientes_list.filter(Q(nombre__icontains=query))
        elif search_field == 'compania':
            clientes_list = clientes_list.filter(Q(compania__icontains=query))
        elif search_field == 'identificacion':
            clientes_list = clientes_list.filter(Q(identificacion__icontains=query))
        elif search_field == 'correo':
            clientes_list = clientes_list.filter(Q(correo__icontains=query))
        elif search_field == 'pais':
            clientes_list = clientes_list.filter(Q(pais__icontains=query))
        else:  # 'all' u otros valores no esperados
            clientes_list = clientes_list.filter(
                Q(nombre__icontains=query) |
                Q(compania__icontains=query) |
                Q(identificacion__icontains=query) |
                Q(correo__icontains=query)
            )

        # Orden preferente por coincidencias de nombre cuando aplique
        if search_field in ['all', 'nombre']:
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
    paginator = Paginator(clientes_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Construir etiqueta legible para estado ("CODE - Name") en cada cliente de la página
    try:
        estados = fetch_us_states()
        code_to_name = {e.get('code'): e.get('name') for e in estados if e.get('code') and e.get('name')}
    except Exception:
        code_to_name = {}

    for c in page_obj:
        code = (c.pais or '').strip()
        if code:
            name = code_to_name.get(code)
            c.estado_label = f"{code} - {name}" if name else code
        else:
            c.estado_label = "No asignado"

    return render(request, 'clientes/lista.html', {
        'page_obj': page_obj,
        'query': query,
        'search_field': search_field,
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
            estados = fetch_us_states()
            return render(request, 'clientes/agregar.html', {
                'form': form,
                'estados': estados
            })
    else:
        form = ClienteForm()
        estados = fetch_us_states()
        return render(request, 'clientes/agregar.html', {
            'form': form,
            'estados': estados
        })


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
            return redirect('detalle_cliente', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)

    # Preparar URL de Google Maps de forma segura (puede ser None)
    maps_url = cliente.google_maps_link
    estados = fetch_us_states()

    return render(request, 'clientes/detalle.html', {
        'cliente': cliente,
        'form': form,
        'maps_url': maps_url,
        'historial': cliente.historial.all().order_by('-fecha_edicion'),
        'puede_editar': puede_editar
        , 'estados': estados
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
