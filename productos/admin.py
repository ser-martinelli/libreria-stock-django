
from django.contrib import admin
from .models import Producto, Categoria

from .models import EntregaInterna, DetalleEntrega

admin.site.register(Producto)
admin.site.register(Categoria)

class DetalleEntregaInline(admin.TabularInline):
    model = DetalleEntrega
    extra = 1


@admin.register(EntregaInterna)
class EntregaInternaAdmin(admin.ModelAdmin):
    list_display = ('id', 'destino', 'fecha')
    inlines = [DetalleEntregaInline]
