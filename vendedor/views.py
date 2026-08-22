from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from tienda.models import Producto, Sabor, ProductoSabor
from .models import Venta, DetalleVenta
from django.utils import timezone
from itertools import zip_longest


class CustomLoginView(LoginView):
    template_name = 'vendedor/login.html'
    def form_invalid(self, form):
        error = "Usuario o contraseña incorrectos."
        return super().form_invalid(form)


@login_required(login_url='/vendedor/login/')
def logout_view(request):
    logout(request)
    return redirect('vendedor:login')


@login_required(login_url='/vendedor/login/')
def panel_vendedor(request):
    productos = Producto.objects.all()
    ventas_recientes = Venta.objects.all().order_by('-fecha')[:5]

    context = {
        'productos': productos,
        'ventas_recientes': ventas_recientes,
    }
    return render(request, 'vendedor/panel.html', context)


@login_required(login_url='/vendedor/login/')
def registrar_venta(request):
    if request.method == 'POST':
        producto_sabor_id = request.POST.get('producto')
        cantidad_vendida = int(request.POST.get('cantidad', 1))

        try:
            prod_sabor = ProductoSabor.objects.get(id=producto_sabor_id)

            if prod_sabor.stock_sabor >= cantidad_vendida:
                total_venta = prod_sabor.producto.precio * cantidad_vendida

                venta = Venta.objects.create(
                    vendedor=request.user,
                    total=total_venta
                )

                DetalleVenta.objects.create(
                    venta=venta,
                    producto=prod_sabor.producto,
                    cantidad=cantidad_vendida,
                    precio_unitario=prod_sabor.producto.precio,
                    subtotal=total_venta
                )

                # Descontar stock del sabor específico
                prod_sabor.stock_sabor -= cantidad_vendida
                prod_sabor.save()

                # Actualizar stock total del producto sumando sus sabores restantes
                total_stock = sum(ps.stock_sabor for ps in prod_sabor.producto.productosabor_set.all())
                prod_sabor.producto.stock = total_stock
                prod_sabor.producto.save()

                return redirect('vendedor:panel')
            else:
                error = f"Stock insuficiente para este sabor. Solo quedan {prod_sabor.stock_sabor} unidades."
                productos_sabores = ProductoSabor.objects.filter(stock_sabor__gt=0)
                return render(request, 'vendedor/registrar_venta.html',
                              {'productos_sabores': productos_sabores, 'error': error})

        except ProductoSabor.DoesNotExist:
            pass

    productos_sabores = ProductoSabor.objects.filter(stock_sabor__gt=0)
    return render(request, 'vendedor/registrar_venta.html', {'productos_sabores': productos_sabores})


# Vista para el panel general de stock y sabores
@staff_member_required
def panel_general(request):
    productos = Producto.objects.all()

    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        sabor_id = request.POST.get('sabor_id')
        cantidad_a_sumar = int(request.POST.get('cantidad', 0))

        if producto_id and sabor_id:
            producto = get_object_or_404(Producto, id=producto_id)
            sabor = get_object_or_404(Sabor, id=sabor_id)

            prod_sabor, creado = ProductoSabor.objects.get_or_create(
                producto=producto,
                sabor=sabor,
                defaults={'stock_sabor': 0}
            )

            prod_sabor.stock_sabor += cantidad_a_sumar
            prod_sabor.save()

            total_stock = sum(ps.stock_sabor for ps in producto.productosabor_set.all())
            producto.stock = total_stock
            producto.save()

            return redirect('vendedor:panel_general')

    context = {
        'productos': productos,
    }
    return render(request, 'vendedor/panel_general.html', context)


@login_required(login_url='/vendedor/login/')
def menu_principal(request):
    hoy = timezone.now().date()

    ventas_hoy = Venta.objects.filter(fecha__date=hoy)
    total_ventas_hoy = sum(v.total for v in ventas_hoy) if ventas_hoy else 0
    cantidad_ventas_hoy = ventas_hoy.count()

    productos = Producto.objects.all()
    productos_disponibles = productos.count()

    stock_total = sum(p.stock for p in productos) if productos else 0
    ventas_recientes = Venta.objects.all().order_by('-fecha')[:5]

    context = {
        'cantidad_ventas_hoy': cantidad_ventas_hoy,
        'total_ventas_hoy': total_ventas_hoy,
        'productos_disponibles': productos_disponibles,
        'stock_total': stock_total,
        'ventas_recientes': ventas_recientes,
    }

    return render(request, 'vendedor/menu_principal.html', context)


def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        # 1. Actualizar datos básicos
        producto.nombre = request.POST.get('nombre', producto.nombre)
        producto.descripcion = request.POST.get('descripcion', producto.descripcion)
        producto.precio = request.POST.get('precio', producto.precio)
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
        producto.save()

        # 2. Lógica para eliminar sabores marcados y actualizar fotos de sabores existentes
        sabores_a_quitar = request.POST.getlist('quitar_sabores')
        if sabores_a_quitar:
            ProductoSabor.objects.filter(producto=producto, sabor_id__in=sabores_a_quitar).delete()

        for ps in producto.productosabor_set.all():
            key_img = f'imagen_sabor_existente_{ps.id}'
            if key_img in request.FILES:
                ps.imagen_sabor = request.FILES[key_img]
                ps.save()

        # 3. Procesar nuevos sabores, cantidades e imágenes dinámicas añadidas
        nombres_sabores = request.POST.getlist('sabores[]')
        cantidades_sabores = request.POST.getlist('cantidades[]')
        imagenes_sabores = request.FILES.getlist('imagens_sabores[]')

        for nombre_sabor, cantidad, img_sabor in zip_longest(nombres_sabores, cantidades_sabores, imagenes_sabores,
                                                             fillvalue=None):
            if nombre_sabor:
                nombre_limpio = nombre_sabor.strip()
                if nombre_limpio:
                    sabor_obj, _ = Sabor.objects.get_or_create(nombre=nombre_limpio)
                    cant_val = int(cantidad) if cantidad and cantidad.isdigit() else 0

                    prod_sabor, creado = ProductoSabor.objects.get_or_create(
                        producto=producto,
                        sabor=sabor_obj,
                        defaults={'stock_sabor': cant_val}
                    )

                    if not creado:
                        prod_sabor.stock_sabor += cant_val

                    if img_sabor:
                        prod_sabor.imagen_sabor = img_sabor

                    prod_sabor.save()

        # 4. Recalcular stock total del producto
        total_stock = sum(ps.stock_sabor for ps in producto.productosabor_set.all())
        producto.stock = total_stock
        producto.save()

        return redirect('vendedor:panel_general')

    return render(request, 'vendedor/editar_producto.html', {'producto': producto})


def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        descripcion = request.POST.get('descripcion', '')
        imagen = request.FILES.get('imagen')

        # 1. Crear el producto base
        producto = Producto.objects.create(
            nombre=nombre,
            precio=precio,
            descripcion=descripcion,
            imagen=imagen
        )

        # 2. Capturar sabores, cantidades e imágenes
        nombres_sabores = request.POST.getlist('sabores[]')
        cantidades_sabores = request.POST.getlist('cantidades[]')
        imagenes_sabores = request.FILES.getlist('imagens_sabores[]')

        for nombre_sabor, cantidad, img_sabor in zip_longest(nombres_sabores, cantidades_sabores, imagenes_sabores,
                                                             fillvalue=None):
            if nombre_sabor:
                nombre_limpio = nombre_sabor.strip()
                if nombre_limpio:
                    sabor_obj, _ = Sabor.objects.get_or_create(nombre=nombre_limpio)
                    cant_val = int(cantidad) if cantidad and cantidad.isdigit() else 0

                    ProductoSabor.objects.create(
                        producto=producto,
                        sabor=sabor_obj,
                        stock_sabor=cant_val,
                        imagen_sabor=img_sabor if img_sabor else None
                    )

        # 3. Calcular stock total inicial
        total_stock = sum(ps.stock_sabor for ps in producto.productosabor_set.all())
        producto.stock = total_stock
        producto.save()

        return redirect('vendedor:panel_general')

    return render(request, 'vendedor/crear_producto.html')


def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    return redirect('vendedor:panel_general')