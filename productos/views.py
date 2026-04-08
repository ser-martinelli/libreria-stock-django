from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Producto

from django.views.generic import TemplateView
from django.db.models import F
from .models import MovimientoStock

from django.views.generic import ListView

import openpyxl
from django.http import HttpResponse
   

class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'productos/list.html'
    context_object_name = 'productos'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Producto.objects.filter(nombre__icontains=query)
        return Producto.objects.all()


class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    fields = '__all__'
    template_name = 'productos/form.html'
    success_url = reverse_lazy('producto_list')


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    fields = '__all__'
    template_name = 'productos/form.html'
    success_url = reverse_lazy('producto_list')


class ProductoDeleteView(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = 'productos/delete.html'
    success_url = reverse_lazy('producto_list')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_productos'] = Producto.objects.count()

        context['bajo_stock'] = Producto.objects.filter(
            stock_actual__lte=F('stock_minimo')
        )

        context['movimientos'] = MovimientoStock.objects.order_by('-fecha')[:5]

        return context





class MovimientoStockCreateView(LoginRequiredMixin, CreateView):
    model = MovimientoStock
    fields = ['producto', 'tipo', 'cantidad']
    template_name = 'productos/movimiento_form.html'
    success_url = reverse_lazy('producto_list')


class MovimientoListView(LoginRequiredMixin, ListView):
    model = MovimientoStock
    template_name = 'productos/movimientos_list.html'
    context_object_name = 'movimientos'
    ordering = ['-fecha']

    def get_queryset(self):
        queryset = super().get_queryset()

        query = self.request.GET.get('q')
        tipo = self.request.GET.get('tipo')

        if query:
            palabras = query.split()

            for palabra in palabras:
                queryset = queryset.filter(producto__nombre__icontains=palabra)

        if tipo:
            queryset = queryset.filter(tipo=tipo)

        return queryset
    

from django.views.generic import CreateView
from .models import MovimientoStock


def export_movimientos_excel(request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Movimientos"

        # Encabezados
        ws.append(["Producto", "Tipo", "Cantidad", "Fecha"])

        movimientos = MovimientoStock.objects.all().order_by('-fecha')

        for mov in movimientos:
            ws.append([
                mov.producto.nombre,
                mov.tipo,
                mov.cantidad,
                mov.fecha.strftime("%d/%m/%Y %H:%M")
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=movimientos.xlsx'

        wb.save(response)
        return response


from django.views.generic import TemplateView
from .models import Categoria

class StockPorCategoriaView(TemplateView):
    template_name = 'productos/stock_categoria.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categorias = Categoria.objects.prefetch_related('producto_set')
        context['categorias'] = categorias

        return context
    

from django.views.generic import ListView
from .models import EntregaInterna

class EntregaListView(LoginRequiredMixin, ListView):
    model = EntregaInterna
    template_name = 'productos/entregas_list.html'
    context_object_name = 'entregas'
    ordering = ['-fecha']


from django.views.generic import DetailView

class EntregaDetailView(LoginRequiredMixin, DetailView):
    model = EntregaInterna
    template_name = 'productos/entrega_detail.html'
    context_object_name = 'entrega'


class EntregaPrintView(LoginRequiredMixin, DetailView):
    model = EntregaInterna
    template_name = 'productos/entrega_print.html'
    context_object_name = 'entrega'


from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse


def generar_pdf_entrega(request, pk):
    entrega = EntregaInterna.objects.get(pk=pk)

    template = get_template('productos/entrega_print.html')
    html = template.render({'entrega': entrega})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="entrega_{entrega.id}.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Producto

@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/lista.html', {'productos': productos})