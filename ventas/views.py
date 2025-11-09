from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncDate
from datetime import date, timedelta, datetime
from .models import Producto, Venta
from django.utils.safestring import mark_safe
import json


def lista_productos(request): # < --- Define la funcion 
    productos = Producto.objects.filter(activo=True) # < ---  Accede al administrador para el modelo producto y filtra los productos que tienen activo nadamas. Tambien lo almacena en Producto
    return render(request, 'ventas/lista_productos.html', {'productos': productos}) # < --- No entiendo muy bien

from datetime import date
from django.db.models import Sum
from django.shortcuts import render

from .models import Producto, Venta

def inicio(request):
    hoy = date.today()

    # Cantidad de productos activos
    productos_activos = Producto.objects.filter(activo=True).count()

    # Ventas de hoy
    ventas_hoy_qs = Venta.objects.filter(fecha_hora__date=hoy)

    # Evita errores si 'total' no es numérico o está vacío
    resumen_hoy = ventas_hoy_qs.aggregate(total_vendido=Sum('total'))
    total_vendido_hoy = resumen_hoy['total_vendido'] or 0

    # Asegura que el valor sea numérico
    try:
        total_vendido_hoy = float(total_vendido_hoy)
    except (ValueError, TypeError):
        total_vendido_hoy = 0

    total_ventas_hoy = ventas_hoy_qs.count()

    contexto = {
        'productos_activos': productos_activos,
        'total_vendido_hoy': total_vendido_hoy,
        'total_ventas_hoy': total_ventas_hoy,
    }

    return render(request, 'ventas/inicio.html', contexto)


def reporte_ventas(request):
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    domingo = lunes + timedelta(days=6)

    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    else:
        fecha_inicio = lunes
        fecha_fin = domingo

    ventas_qs = Venta.objects.filter(
        fecha_hora__date__gte=fecha_inicio,
        fecha_hora__date__lte=fecha_fin
    )

    ventas_por_dia = (
        ventas_qs
        .annotate(dia=TruncDate('fecha_hora'))
        .values('dia')
        .annotate(
            total_vendido=Sum('total'),
            unidades_vendidas=Sum('detalles__cantidad')
        )
        .order_by('dia')
    )

    total_periodo = ventas_qs.aggregate(
        total_vendido=Sum('total'),
        unidades_vendidas=Sum('detalles__cantidad')
    )

    # 👉 Datos para el gráfico
    labels = []
    data = []
    for v in ventas_por_dia:
        # Etiqueta: día en formato corto
        labels.append(v['dia'].strftime('%A'))  # Sunday, Monday... (puedes cambiarlo)
        # Valor numérico
        data.append(float(v['total_vendido'] or 0))

    contexto = {
        'ventas_por_dia': ventas_por_dia,
        'total_periodo': total_periodo,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        # estos van directo al JS
        'chart_labels': mark_safe(json.dumps(labels)),
        'chart_data': mark_safe(json.dumps(data)),
    }
    return render(request, 'ventas/reporte_ventas.html', contexto)
