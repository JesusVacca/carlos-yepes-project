from django.contrib import admin
from .models import Producto, Sabor, ProductoSabor

admin.site.register(Producto)
admin.site.register(Sabor)
admin.site.register(ProductoSabor)