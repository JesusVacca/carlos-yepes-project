from django.urls import path
from . import views

app_name = 'vendedor'

urlpatterns = [
    path('', views.registrar_venta, name='index'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('panel/', views.panel_vendedor, name='panel'),
    path('registrar-venta/', views.registrar_venta, name='registrar_venta'),
    path('panel-general/', views.panel_general, name='panel_general'),
    path('menu/', views.menu_principal, name='menu_principal'),
    path('logout/', views.logout_view, name='logout'),
    path('editar-producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('crear-producto/', views.crear_producto, name='crear_producto'),
    path('producto/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
]