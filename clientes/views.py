from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .models import Cliente
from .forms import ClienteForm

@login_required
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista.html', {'clientes': clientes})

@permission_required('clientes.add_cliente', raise_exception=False)
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'clientes/agregar.html', {'form': form})

@permission_required('clientes.delete_cliente', raise_exception=False)
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    # ideal: confirmar con POST; aquí borramos directamente para simplicidad
    cliente.delete()
    return redirect('lista_clientes')
