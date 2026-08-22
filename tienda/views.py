from django.views.generic import ListView, DetailView

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Producto, Sabor, ProductoSabor


class Home(ListView):
    model = Producto
    template_name = 'tienda/inicio.html'
    context_object_name = 'productos'
    def get_queryset(self):
        return Producto.objects.filter(disponible=True)


class ProductDetailsView(DetailView):
    model = Producto
    slug_field = 'id'
    slug_url_kwarg = 'id'
    context_object_name = 'producto'
    template_name = 'tienda/detalle_producto.html'


# Vista para administrar los ingresos y stock por sabor
@staff_member_required
def gestionar_stock(request):
    productos = Producto.objects.all()

    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        sabor_id = request.POST.get('sabor_id')
        cantidad_a_sumar = int(request.POST.get('cantidad', 0))

        producto = get_object_or_404(Producto, id=producto_id)
        sabor = get_object_or_404(Sabor, id=sabor_id)

        # Buscar o crear la relación del sabor para este producto
        prod_sabor, creado = ProductoSabor.objects.get_or_create(
            producto=producto,
            sabor=sabor,
            defaults={'stock_sabor': 0}
        )

        # Sumar las unidades nuevas que llegaron
        prod_sabor.stock_sabor += cantidad_a_sumar
        prod_sabor.save()

        # Actualizar el stock total del producto sumando todos sus sabores
        total_stock = sum(ps.stock_sabor for ps in producto.productosabor_set.all())
        producto.stock = total_stock
        producto.save()

        return redirect('gestionar_stock')

    return render(request, 'tienda/gestionar_stock.html', {'productos': productos})