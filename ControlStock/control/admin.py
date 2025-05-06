
from django.utils.html import format_html  # Importa la función para generar HTML seguro.
from .models import Categoria, Ubicacion, Producto, MovimientoStock  # Importa los modelos definidos en el mismo directorio (app).

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado


class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'rol', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'telefono')}),
        ('Permisos', {
            'fields': ('rol', 'is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(UsuarioPersonalizado, UsuarioAdmin)
@admin.register(Categoria)  # Decorador para registrar la clase CategoriaAdmin con el panel de administración.
class CategoriaAdmin(admin.ModelAdmin):
    """
    Clase para personalizar la interfaz de administración del modelo Categoria.
    """
    list_display = ('nombre', 'color_display', 'producto_count')  # Define los campos a mostrar en la lista de categorías.
    search_fields = ('nombre',)  # Permite buscar categorías por su nombre.

    def color_display(self, obj):
        """
        Método para mostrar visualmente el color de la categoría en la lista.
        Utiliza format_html para renderizar un div con el color de fondo.
        """
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {};"></div>',
            obj.color  # Obtiene el valor del campo 'color' del objeto Categoria.
        )
    color_display.short_description = 'Color'  # Define el nombre de la columna en la lista.

    def producto_count(self, obj):
        """
        Método para mostrar la cantidad de productos asociados a cada categoría.
        Accede a través de la relación inversa 'producto_set'.
        """
        return obj.producto_set.count()  # Cuenta los productos relacionados con la categoría.
    producto_count.short_description = 'Productos'  # Define el nombre de la columna en la lista.


@admin.register(Ubicacion)  # Decorador para registrar la clase UbicacionAdmin con el panel de administración.
class UbicacionAdmin(admin.ModelAdmin):
    """
    Clase para personalizar la interfaz de administración del modelo Ubicacion.
    """
    list_display = ('nombre', 'codigo', 'descripcion_corta')  # Define los campos a mostrar en la lista de ubicaciones.
    search_fields = ('nombre', 'codigo')  # Permite buscar ubicaciones por su nombre o código.

    def descripcion_corta(self, obj):
        """
        Método para mostrar una versión abreviada de la descripción de la ubicación en la lista.
        Si la descripción existe, la trunca a 50 caracteres y añade '...'.
        """
        return obj.descripcion[:50] + '...' if obj.descripcion else ''
    descripcion_corta.short_description = 'Descripción'  # Define el nombre de la columna en la lista.


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Clase para personalizar la interfaz de administración del modelo Producto.
    """
    list_display = ('codigo_barras', 'nombre', 'categoria', 'stock_display',
                    'estado_display', 'precio_compra', 'precio_venta', 'activo')
    list_filter = ('categoria', 'estado', 'activo')
    search_fields = ('codigo_barras', 'nombre', 'descripcion')  # Cambiado de 'codigo'
    readonly_fields = ('qr_preview', 'creado', 'actualizado')
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo_barras', 'nombre', 'descripcion', 'activo')  # Eliminado 'codigo'
        }),
        ('Categorización', {
            'fields': ('categoria', 'ubicacion')
        }),
        ('Precios y Stock', {
            'fields': ('precio_compra', 'precio_venta', 'stock_actual', 'stock_minimo', 'estado')
        }),
        ('Imágenes', {
            'fields': ('imagen', 'qr_preview')
        }),
        ('Auditoría', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )

    def stock_display(self, obj):
        color = 'green'
        if obj.estado == 'BAJO':
            color = 'orange'
        elif obj.estado == 'AGOTADO':
            color = 'red'
        return format_html(
            '<span style="color: {};">{}</span> / {}',
            color, obj.stock_actual, obj.stock_minimo
        )
    stock_display.short_description = 'Stock (Actual/Mín)'

    def estado_display(self, obj):
        colors = {
            'OK': 'green',
            'BAJO': 'orange',
            'AGOTADO': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors[obj.estado], obj.get_estado_display()
        )
    estado_display.short_description = 'Estado'

    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" style="max-height: 100px;" />',
                obj.qr_code.url
            )
        return "No generado"
    qr_preview.short_description = 'Código QR'

@admin.register(MovimientoStock)  # Decorador para registrar la clase MovimientoStockAdmin con el panel de administración.
class MovimientoStockAdmin(admin.ModelAdmin):
    """
    Clase para personalizar la interfaz de administración del modelo MovimientoStock.
    """
    list_display = ('fecha', 'producto', 'tipo_display', 'cantidad',
                    'ubicaciones_display', 'usuario')  # Campos a mostrar en la lista de movimientos de stock.
    list_filter = ('tipo', 'fecha', 'producto__categoria')  # Permite filtrar la lista por tipo de movimiento, fecha y categoría del producto.
    search_fields = ('producto__nombre', 'producto__codigo', 'observaciones')  # Permite buscar movimientos por nombre o código del producto y observaciones.
    date_hierarchy = 'fecha'  # Permite navegar por los movimientos por jerarquía de fechas (año, mes, día).
    readonly_fields = ('fecha', 'usuario')  # Campos que se mostrarán solo para lectura en el formulario de edición.

    def tipo_display(self, obj):
        """
        Método para mostrar el tipo de movimiento con un color asociado.
        Verde para ENTRADA, rojo para SALIDA, azul para AJUSTE y morado para TRASPASO.
        """
        colors = {
            'ENTRADA': 'green',
            'SALIDA': 'red',
            'AJUSTE': 'blue',
            'TRASPASO': 'purple'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors[obj.tipo], obj.get_tipo_display()  # Obtiene la representación legible del tipo de movimiento.
        )
    tipo_display.short_description = 'Tipo'  # Define el nombre de la columna en la lista.

    def ubicaciones_display(self, obj):
        """
        Método para mostrar las ubicaciones de origen y destino de un movimiento de stock, dependiendo del tipo.
        Para TRASPASO muestra ambas, para ENTRADA solo el destino, para SALIDA solo el origen.
        """
        if obj.tipo == 'TRASPASO':
            return f"{obj.ubicacion_origen} → {obj.ubicacion_destino}"
        elif obj.tipo == 'ENTRADA':
            return f"→ {obj.ubicacion_destino}"
        elif obj.tipo == 'SALIDA':
            return f"{obj.ubicacion_origen} →"
        return "-"  # Para otros tipos de movimiento o si no hay ubicaciones definidas.
    ubicaciones_display.short_description = 'Ubicaciones'  # Define el nombre de la columna en la lista.

    def save_model(self, request, obj, form, change):
        """
        Método para guardar un movimiento de stock en la base de datos.
        Si el movimiento es nuevo (no tiene pk), asigna automáticamente el usuario que realizó la acción.
        """
        if not obj.pk:  # Solo para nuevos movimientos
            obj.usuario = request.user  # Asigna el usuario actual al campo 'usuario' del movimiento.
        super().save_model(request, obj, form, change)  # Llama al método save_model de la clase padre para guardar el objeto.