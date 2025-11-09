from django.urls import path
from . import views

urlpatterns = [
    # Página de inicio: lista de productos
    path('', views.inicio, name='inicio'),

    # Lista de productos
    path('productos/', views.lista_productos, name='lista_productos'),

    # Reporte de ventas
    path('reportes/ventas/', views.reporte_ventas, name='reporte_ventas'),
]
