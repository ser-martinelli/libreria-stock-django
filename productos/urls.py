
from django.urls import path
from .views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
    EntregaDetailView,
    EntregaPrintView
)
from .views import DashboardView
from .views import MovimientoStockCreateView

from .views import MovimientoListView

from .views import export_movimientos_excel

from .views import StockPorCategoriaView

from .views import EntregaListView

from .views import generar_pdf_entrega

from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', ProductoListView.as_view(), name='producto_list'),
    path('nuevo/', ProductoCreateView.as_view(), name='producto_create'),
    path('editar/<int:pk>/', ProductoUpdateView.as_view(), name='producto_update'),
    path('eliminar/<int:pk>/', ProductoDeleteView.as_view(), name='producto_delete'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('movimiento/', MovimientoStockCreateView.as_view(), name='movimiento_create'),
    path('movimientos/', MovimientoListView.as_view(), name='movimientos_list'),
    path('movimientos/excel/', export_movimientos_excel, name='export_excel'),
    path('stock-categorias/', StockPorCategoriaView.as_view(), name='stock_categoria'),
    path('entregas/', EntregaListView.as_view(), name='entregas_list'),
    path('entregas/<int:pk>/', EntregaDetailView.as_view(), name='entrega_detail'),
    path('entregas/<int:pk>/print/', EntregaPrintView.as_view(), name='entrega_print'),
    path('entregas/<int:pk>/pdf/', generar_pdf_entrega, name='entrega_pdf'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
]