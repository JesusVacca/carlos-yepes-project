from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='inicio'),
    path('producto/<int:id>/', views.ProductDetailsView.as_view(), name='detalle_producto'),
    path('stock/', views.gestionar_stock, name='gestionar_stock'),
]