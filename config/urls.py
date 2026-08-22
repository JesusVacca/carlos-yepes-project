from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Esta es tu ruta de tienda
    path('', include('tienda.urls')),

    # Esta es tu ruta para el panel del vendedor
    path('vendedor/', include('vendedor.urls')),
]

# Configuración para servir archivos estáticos (CSS, JS, imágenes del logo)
# y archivos media (fotos de productos) durante el desarrollo.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)