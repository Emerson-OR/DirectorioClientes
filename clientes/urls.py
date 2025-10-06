from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
]
