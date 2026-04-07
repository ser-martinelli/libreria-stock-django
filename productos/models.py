from django.db import models

from django.core.exceptions import ValidationError

from django.views.generic import TemplateView




class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo} - {self.cantidad}"
    
    def clean(self):
        if self.tipo == 'salida' and self.producto.stock_actual < self.cantidad:
            raise ValidationError('No hay stock suficiente para realizar esta salida')


    def save(self, *args, **kwargs):
        self.full_clean()  # 👈 ESTO ES CLAVE

        if self.tipo == 'entrada':
            self.producto.stock_actual += self.cantidad
        elif self.tipo == 'salida':
            self.producto.stock_actual -= self.cantidad

        self.producto.save()
        super().save(*args, **kwargs)


class StockPorCategoriaView(TemplateView):
    template_name = 'productos/stock_categoria.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categorias = Categoria.objects.prefetch_related('producto_set')

        context['categorias'] = categorias

        return context
    

class EntregaInterna(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    destino = models.CharField(max_length=150)
    observacion = models.TextField(blank=True)

    def __str__(self):
        return f"Entrega a {self.destino} - {self.fecha.strftime('%d/%m/%Y')}"


class DetalleEntrega(models.Model):
    entrega = models.ForeignKey(EntregaInterna, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"

    def save(self, *args, **kwargs):
        # ❗ VALIDACIÓN
        if self.producto.stock_actual < self.cantidad:
            raise ValueError(f"No hay stock suficiente para {self.producto.nombre}")

        # 🔻 DESCUENTA STOCK
        self.producto.stock_actual -= self.cantidad
        self.producto.save()

        # 📦 CREA MOVIMIENTO
        MovimientoStock.objects.create(
            producto=self.producto,
            tipo='salida',
            cantidad=self.cantidad,
        )

        super().save(*args, **kwargs)
