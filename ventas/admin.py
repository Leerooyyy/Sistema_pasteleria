from django.contrib import admin
from .models import Categoria, Producto, Venta, DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    # NO usamos readonly_fields aquí, para que el JS pueda escribir en el input
    # readonly_fields = ('subtotal',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

class Media:
        # ruta dentro de static: ventas/js/detalle_venta.js
        js = ('ventas/js/detalle_venta.js',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'precio_venta', 'stock_actual', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_hora', 'usuario', 'total', 'metodo_pago')
    list_filter = ('metodo_pago', 'fecha_hora')
    search_fields = ('usuario__username',)
    date_hierarchy = 'fecha_hora'
    inlines = [DetalleVentaInline]
