from django.db import models

class Sabor(models.Model):
    nombre = models.CharField(max_length=100)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0) # Stock total (suma de todos los sabores)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    sabores = models.ManyToManyField(Sabor, through='ProductoSabor', blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre

# Tabla intermedia que guarda stock y la foto específica de cada sabor por producto
class ProductoSabor(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    sabor = models.ForeignKey(Sabor, on_delete=models.CASCADE)
    stock_sabor = models.PositiveIntegerField(default=0) # Unidades específicas de este sabor
    imagen_sabor = models.ImageField(upload_to='sabores_productos/', blank=True, null=True) # Foto exclusiva de este sabor

    def __str__(self):
        return f"{self.producto.nombre} - {self.sabor.nombre} ({self.stock_sabor} un.)"