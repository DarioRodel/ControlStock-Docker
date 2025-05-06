# Importaciones necesarias para los modelos y funciones auxiliares
from typing import Any  # Tipado genérico para mayor claridad.
from django.db import models  # Base para definir modelos en Django.
from django.contrib.auth.models import User, AbstractUser, Group  # Para extender y usar el sistema de usuarios.
from django.urls import reverse  # Permite construir URLs a partir del nombre de la vista.
from django.core.validators import MinValueValidator  # Validador para asegurar que ciertos campos no tengan valores negativos.
import qrcode  # Librería para generar códigos QR.
from io import BytesIO  # Para trabajar con archivos en memoria.
from django.core.files import File  # Para guardar archivos en campos FileField o ImageField.
from django.conf import settings  # Acceso a la configuración global de Django.

# Modelo para representar categorías de productos
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # Nombre único de la categoría.
    descripcion = models.TextField(blank=True)  # Descripción opcional.
    total_stock = models.IntegerField(default=0)  # Acumulado de stock de todos los productos de esta categoría.
    color = models.CharField(max_length=7, default='#4e73df')  # Color en formato HEX, útil para gráficos.

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']  # Orden alfabético.

    def __str__(self):
        return self.nombre  # Para mostrar el nombre directamente en interfaces de administración.


# Modelo para representar ubicaciones físicas del inventario
class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre descriptivo de la ubicación.
    codigo = models.CharField(max_length=10, unique=True)  # Código corto e identificador.
    descripcion = models.TextField(blank=True)  # Descripción opcional.

    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"  # Ej: “Almacén A (A1)”


# Modelo principal que representa productos
class Producto(models.Model):
    # Opciones de estado del stock
    ESTADO_STOCK = (
        ('NORMAL', 'Stock Normal'),
        ('BAJO', 'Stock Bajo'),
        ('AGOTADO', 'Stock Agotado'),
    )

    codigo_barras = models.CharField(max_length=100, unique=True, verbose_name='Código de Barras')
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(blank=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_actual = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.IntegerField(default=5, validators=[MinValueValidator(0)])
    estado = models.CharField(max_length=10, choices=ESTADO_STOCK, default='NORMAL')
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='productos_qr/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)  # Se establece automáticamente al crear.
    actualizado = models.DateTimeField(auto_now=True)  # Se actualiza automáticamente cada vez que se guarda.

    class Meta:
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['codigo_barras']),
            models.Index(fields=['categoria']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.codigo_barras})"

    # Método para generar el código QR
    def generate_qrcode(self):
        if not self.id:
            self.save()  # Se asegura de que el producto ya tiene ID antes de generar el QR.

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"PROD:{self.id}:{self.codigo_barras}")  # Información que se codificará en el QR.
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer)
        filename = f'qr_{self.codigo_barras}.png'
        self.qr_code.save(filename, File(buffer), save=False)  # Asigna el archivo generado al campo qr_code.

    # Método sobrescrito para generar código QR automáticamente
    def save(self, *args, **kwargs):
        if not self.codigo_barras:
            self.codigo_barras = self.codigo  # Esto parece redundante, ya que no hay un campo llamado 'codigo'
        super().save(*args, **kwargs)

        if not self.qr_code:
            self.generate_qrcode()
            super().save(*args, **kwargs)

    # Método para generar la URL de detalle del producto
    def get_absolute_url(self):
        return reverse('detalle_producto', kwargs={'pk': self.pk})

    # Calcula el valor total del inventario de este producto
    @property
    def valor_inventario(self):
        return self.stock_actual * self.precio_compra


# Modelo que registra cada movimiento de stock
class MovimientoStock(models.Model):
    TIPO_MOVIMIENTO = (
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
        ('TRASPASO', 'Traspaso'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    ubicacion_origen = models.ForeignKey(
        Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_salida')
    ubicacion_destino = models.ForeignKey(
        Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_entrada')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.cantidad} {self.producto} - {self.fecha}"

    # Actualiza el stock del producto si el movimiento es nuevo
    def save(self, *args, **kwargs):
        if not self.pk:  # Solo si es un nuevo movimiento
            if self.tipo == 'ENTRADA':
                self.producto.stock_actual += self.cantidad
            elif self.tipo == 'SALIDA':
                self.producto.stock_actual -= self.cantidad
            self.producto.save()
        super().save(*args, **kwargs)


# Usuario personalizado que hereda del usuario por defecto de Django
class UsuarioPersonalizado(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('gestor', 'Gestor de categorías'),
        ('ventas', 'Equipo de Ventas'),
    )

    rol = models.CharField(max_length=20, choices=ROLES, default='almacen')
    telefono = models.CharField(max_length=20, blank=True)
    departamento = models.CharField(max_length=50, blank=True)

    class Meta:
        permissions = [
            ("puede_ver_reportes", "Puede ver reportes avanzados"),
            ("puede_gestionar_usuarios", "Puede gestionar usuarios"),
            ("puede_eliminar_productos", "Puede eliminar productos"),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.rol})"
