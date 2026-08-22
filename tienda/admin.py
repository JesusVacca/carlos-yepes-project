from django.contrib import admin
from .models import Producto, Sabor, ProductoSabor

class ProductoSaborInline(admin.TabularInline):
    model = ProductoSabor
    extra = 1

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'disponible', 'fecha_creacion')
    inlines = [ProductoSaborInline]

@admin.register(Sabor)
class SaborAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'disponible')