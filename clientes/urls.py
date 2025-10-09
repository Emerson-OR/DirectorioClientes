from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('registro/', views.registro, name='registro'),  # <--- Aquí
    path('clientes/<int:pk>/', views.detalle_cliente, name='detalle_cliente'),
    path('eliminados/', views.clientes_eliminados, name='clientes_eliminados'),
    path('restaurar/<int:pk>/', views.restaurar_cliente, name='restaurar_cliente'),

]
