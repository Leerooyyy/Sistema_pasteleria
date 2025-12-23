from datetime import date, timedelta, datetime
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils.safestring import mark_safe

from .models import Producto, Venta



@login_required
def inicio(request):
    hoy = date.today()

    # Cantidad de productos activos
    productos_activos = Producto.objects.filter(activo=True).count()

    # Ventas de hoy
    ventas_hoy_qs = Venta.objects.filter(fecha_hora__date=hoy)

    # Total vendido hoy
    total_vendido_hoy = ventas_hoy_qs.aggregate(total_vendido=Sum("total"))["total_vendido"] or 0

    # Asegurar numérico (por si viene Decimal)
    try:
        total_vendido_hoy = float(total_vendido_hoy)
    except (ValueError, TypeError):
        total_vendido_hoy = 0

    total_ventas_hoy = ventas_hoy_qs.count()

    contexto = {
        "productos_activos": productos_activos,
        "total_vendido_hoy": total_vendido_hoy,
        "total_ventas_hoy": total_ventas_hoy,
    }
    return render(request, "ventas/inicio.html", contexto)


@login_required
@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, "ventas/lista_productos.html", {"productos": productos})


@login_required
def reporte_ventas(request):
    fecha_inicio_str = request.GET.get("fecha_inicio")
    fecha_fin_str = request.GET.get("fecha_fin")

    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    domingo = lunes + timedelta(days=6)

    # Si el usuario filtra fechas, las usamos; si no, usamos semana actual
    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    else:
        fecha_inicio = lunes
        fecha_fin = domingo

    ventas_qs = Venta.objects.filter(
        fecha_hora__date__gte=fecha_inicio,
        fecha_hora__date__lte=fecha_fin
    )

    ventas_por_dia = (
        ventas_qs
        .annotate(dia=TruncDate("fecha_hora"))
        .values("dia")
        .annotate(
            total_vendido=Sum("total"),
            unidades_vendidas=Sum("detalles__cantidad"),
        )
        .order_by("dia")
    )

    total_periodo = ventas_qs.aggregate(
        total_vendido=Sum("total"),
        unidades_vendidas=Sum("detalles__cantidad"),
    )

    # Datos para el gráfico
    labels = []
    data = []

    # Días en español (para que se vea bonito y consistente)
    dias_es = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }

    for v in ventas_por_dia:
        dia_dt = v["dia"]
        dia_en = dia_dt.strftime("%A")
        labels.append(dias_es.get(dia_en, dia_en))

        total = v["total_vendido"] or 0
        try:
            data.append(float(total))
        except (ValueError, TypeError):
            data.append(0)

    contexto = {
        "ventas_por_dia": ventas_por_dia,
        "total_periodo": total_periodo,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "chart_labels": mark_safe(json.dumps(labels)),
        "chart_data": mark_safe(json.dumps(data)),
    }
    return render(request, "ventas/reporte_ventas.html", contexto)
def ventas(request):
    # Para mostrar el select de productos en el formulario
    productos = Producto.objects.filter(activo=True)

    if request.method == "POST":
        producto_id = request.POST.get("producto")
        cantidad = request.POST.get("cantidad")
        cliente = request.POST.get("cliente", "Venta Mostrador")

        # Validaciones básicas
        try:
            producto = Producto.objects.get(id=producto_id)
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except Exception:
            messages.error(request, "Producto o cantidad inválida.")
            return render(request, "ventas/ventas.html", {"productos": productos})

        # Calcula total (ajusta si tu campo de precio se llama diferente)
        precio_unit = float(producto.precio)
        total = precio_unit * cantidad

        # ⚠️ Esto guarda una venta simple (1 producto).
        # Si tu modelo Venta requiere más campos obligatorios, dime cuáles y lo ajusto.
        Venta.objects.create(
            cliente=cliente,
            total=total,
            fecha_hora=timezone.now(),
        )

        messages.success(request, "Venta registrada.")
        return redirect("ventas")

    return render(request, "ventas/ventas.html", {"productos": productos})

