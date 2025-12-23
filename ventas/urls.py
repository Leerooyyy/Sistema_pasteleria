from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from . import views

def root_redirect(request):
    return redirect('login')

urlpatterns = [
    path('', root_redirect),                # / → login
    path('inicio/', views.inicio, name='inicio'),  # 👈 dashboard real
    path('ventas/', views.ventas, name='ventas'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('reportes/', views.reporte_ventas, name='reporte_ventas'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
