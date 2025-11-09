from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models import Sum

# La cantidad de productos que venderemos en la pastelería/dulcería
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre # <--- Si el nombre es "Pasteles" arriba, Aca saldra 'Pasteles' = 1.

# Las cosas que venden la pastelería.
class Producto(models.Model):
    nombre = models.CharField(max_length=150) # <---- Nombre del producto
    categoria = models.ForeignKey(    # <---- Relacion muchos a uno. Muchos productos pertenecer a una categoria
        Categoria,
        on_delete = models.SET_NULL, # <---La categoria se pone a null
        null = True,  # <--- En la base de datos se permite null
        blank = True  # <--- En formularios puedes dejarlo en blanco
    )

    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)  # <--- Numero decimal exacto, mejor que el float y el decimal_places=2 siempre 2 decimales
    stock_actual = models.IntegerField(default=0)  # <--- Representa cuantas unidades tienes actualmente
    activo = models.BooleanField(default=True)  # <--- Sirve para ocultar un producto Verdadero/falso.

    def __str__(self):
        return self.nombre


class Venta(models.Model): 
    # fecha y hora para luego agrupar por día/semana
    fecha_hora = models.DateTimeField(auto_now_add=True) # <--- Sirve para hacer los reportes diarios/semanales
    usuario = models.ForeignKey( # <--- La persona que hizo la venta
        User,
        on_delete=models.SET_NULL, # < --- Si se borra el usuario, la venta queda como null
        null=True, # < --- En la base de datos te permite dejarlo en null
        blank=True # < --- Campo opcional... que puedes dejar en blanco.
    )

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0) # < --- Monto total de la venta
    metodo_pago = models.CharField(max_length=50, default='Efectivo') # < --- Sirve para Decir como fue el metodo de pago

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_hora}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        related_name='detalles',
        on_delete=models.CASCADE
    )
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        # Por seguridad, se recalcula siempre en el backend
        if self.cantidad is None:
            self.cantidad = 0
        if self.precio_unitario is None and self.producto:
            self.precio_unitario = self.producto.precio_venta

        self.subtotal = (self.precio_unitario or Decimal('0')) * self.cantidad
        super().save(*args, **kwargs)

        # Actualizar total de la venta
        if self.venta_id:
            total = self.venta.detalles.aggregate(
                total=Sum('subtotal')
            )['total'] or Decimal('0')
            self.venta.total = total
            self.venta.save(update_fields=['total'])

#self → es el objeto actual (por ejemplo, el detalle de una venta).

#self.producto → accede al producto asociado (relación ForeignKey).

#self.producto.nombre → accede al nombre del producto.

#self.cantidad → la cantidad vendida en ese detalle.

#La f antes de las comillas (f"...") → indica que es una f-string (formateo de texto).