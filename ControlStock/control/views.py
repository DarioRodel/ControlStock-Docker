from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render  # Importa la función redirect para redireccionar a otras URLs.
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView  # Importa vistas genéricas de Django.
from django.urls import reverse_lazy  # Importa reverse_lazy para generar URLs de forma diferida.
from django.contrib import messages  # Importa el sistema de mensajes de Django para mostrar notificaciones al usuario.
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .forms import ProductoForm, ReporteErrorForm  # Importa los formularios de la aplicación.
from django.views.generic.edit import FormView  # Importa la vista genérica para manejar formularios.
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Producto, MovimientoStock, Categoria
from django.db.models import Sum, F
from django.views.generic import TemplateView
from rest_framework.views import APIView
from django.contrib.auth.mixins import PermissionRequiredMixin


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'stock/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener todos los productos
        productos = Producto.objects.all()

        # Obtener los últimos 10 movimientos de stock
        movimientos = MovimientoStock.objects.select_related('producto', 'usuario').order_by('-fecha')[:10]

        # Contar total de productos y categorías
        total_productos = productos.count()
        total_categorias = Categoria.objects.count()

        # Calcular el valor total del inventario
        valor_total_inventario = productos.aggregate(
            total=Sum(F('precio_compra') * F('stock_actual'))
        )['total'] or 0

        # Obtener productos con stock bajo
        productos_bajo_stock = Producto.objects.filter(stock_actual__lt=10)

        # Datos para el gráfico
        categorias = Categoria.objects.all()
        categorias_data = []  # Lista de datos para el gráfico

        for categoria in categorias:
            total_stock = productos.filter(categoria=categoria).aggregate(total=Sum('stock_actual'))['total'] or 0
            categorias_data.append({
                'nombre': categoria.nombre,
                'total_stock': total_stock,
                'color': categoria.color or '#4F46E5'  # Usar color predeterminado si no hay color
            })

        categorias_nombres = [categoria['nombre'] for categoria in categorias_data]
        categorias_stock = [categoria['total_stock'] for categoria in categorias_data]
        categorias_colores = [categoria['color'] for categoria in categorias_data]

        context.update({
            'total_productos': total_productos,
            'total_categorias': total_categorias,
            'valor_inventario': valor_total_inventario,
            'productos_bajo_stock': productos_bajo_stock,
            'movimientos': movimientos,
            'categorias_nombres': categorias_nombres,
            'categorias_stock': categorias_stock,
            'categorias_colores': categorias_colores,
        })
        estados = dict(Producto.ESTADO_STOCK)
        estado_counts = {
            'NORMAL': productos.filter(estado='NORMAL').count(),
            'BAJO': productos.filter(estado='BAJO').count(),
            'AGOTADO': productos.filter(estado='AGOTADO').count(),
        }

        context.update({
            'stock_estados_labels': [estados['NORMAL'], estados['BAJO'], estados['AGOTADO']],
            'stock_estados_data': [estado_counts['NORMAL'], estado_counts['BAJO'], estado_counts['AGOTADO']],
            'stock_estados_colors': ['#4CAF50', '#FF9800', '#F44336'],  # verde, naranja, rojo
        })
        return context

    def _enviar_notificacion_stock_bajo(self):
        productos_bajo_stock = Producto.objects.filter(stock_actual__lt=10)
        for producto in productos_bajo_stock:
            send_mail(
                'Alerta de stock bajo',
                f'El producto {producto.nombre} tiene un stock bajo.',
                'admin@miempresa.com',
                ['gerente@miempresa.com'],
            )


# Vistas para Productos
class ProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Vista para listar todos los productos. Requiere que el usuario esté logueado.
    Permite filtrar y paginar los productos.
    """
    permission_required = 'control.view_producto'
    model = Producto
    template_name = 'stock/producto_list.html'  # Plantilla para mostrar la lista de productos.
    context_object_name = 'productos'  # Nombre de la variable en el contexto de la plantilla.
    paginate_by = 20  # Cantidad de productos por página.

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol not in ['admin', 'ventas']:
            return render(request, 'stock/403.html',
                          {'message': "No tienes permisos para acceder a esta página."},
                          status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Obtiene el conjunto de productos a mostrar, aplicando filtros si es necesario.
        """
        queryset = super().get_queryset()
        # Filtros basados en los parámetros GET de la request.
        search = self.request.GET.get('search')
        categoria = self.request.GET.get('categoria')
        estado = self.request.GET.get('estado')

        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) |  # Busca por código (insensible a mayúsculas/minúsculas).
                Q(nombre__icontains=search) |  # Busca por nombre.
                Q(descripcion__icontains=search)  # Busca por descripción.
            )

        if categoria:
            queryset = queryset.filter(categoria__id=categoria)  # Filtra por ID de categoría.

        if estado:
            queryset = queryset.filter(estado=estado)  # Filtra por estado del stock.

        return queryset.select_related('categoria', 'ubicacion')  # Mejora el rendimiento al obtener datos relacionados.

    def get_context_data(self, **kwargs):
        """
        Añade al contexto las categorías y los estados de stock para los filtros.
        """
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()  # Obtiene todas las categorías para el filtro.
        context['estados'] = Producto.ESTADO_STOCK  # Obtiene las opciones de estado para el filtro.
        return context


class ProductoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Vista para mostrar los detalles de un producto específico. Requiere login.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol not in ['admin', 'ventas']:
            return render(request, 'stock/403.html',
                          {'message': "No tienes permisos para acceder a esta página."},
                          status=403)
        return super().dispatch(request, *args, **kwargs)

    permission_required = 'stock.change_producto'
    model = Producto
    template_name = 'stock/producto_detail.html'  # Plantilla para los detalles del producto.
    context_object_name = 'producto'  # Nombre de la variable del producto en el contexto.

    def get_context_data(self, **kwargs):
        """
        Añade al contexto los últimos 10 movimientos de stock del producto.
        """
        context = super().get_context_data(**kwargs)
        context['movimientos'] = self.object.movimientos.all()[:10]  # Obtiene los últimos 10 movimientos relacionados.
        return context


class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Vista para crear un nuevo producto. Requiere login y utiliza un formulario.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol not in ['admin', 'ventas']:
            return render(request, 'stock/403.html',
                          {'message': "No tienes permisos para acceder a esta página."},
                          status=403)
        return super().dispatch(request, *args, **kwargs)

    permission_required = 'control.add_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'stock/producto_create.html'
    success_url = reverse_lazy('stock:producto_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        producto = self.object
        initial_stock = producto.stock_actual

        MovimientoStock.objects.create(
            producto=producto,
            tipo='ENTRADA',
            cantidad=initial_stock,
            usuario=self.request.user,
            observaciones='Registro de creación de producto'
        )

        producto.refresh_from_db()
        if producto.stock_actual != initial_stock:
            producto.stock_actual = initial_stock
            producto.save()

        messages.success(self.request, 'Producto creado y movimiento registrado correctamente.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Puedes agregar más datos al contexto si es necesario
        context['fields'] = ['codigo', 'nombre', 'precio_compra', 'precio_venta', 'codigo_barras']
        return context


class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Vista para editar un producto existente. Requiere login y utiliza un formulario.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol not in ['admin', 'ventas']:
            return render(request, 'stock/403.html',
                          {'message': "No tienes permisos para acceder a esta página."},
                          status=403)
        return super().dispatch(request, *args, **kwargs)

    permission_required = 'control.change_producto'
    model = Producto
    form_class = ProductoForm  # Formulario para la edición del producto.
    template_name = 'stock/producto_create.html'  # Utiliza la misma plantilla que la creación.
    success_url = reverse_lazy('stock:producto_list')  # URL a la que se redirige tras la edición exitosa.

    def form_valid(self, form):
        """
        Muestra un mensaje de éxito tras la actualización.
        """
        messages.success(self.request, 'Producto actualizado correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Añade al contexto los campos del formulario para la plantilla.
        """
        context = super().get_context_data(**kwargs)
        context['fields'] = ['codigo', 'nombre', 'precio_compra', 'precio_venta']
        return context


class MovimientoStockCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear un nuevo movimiento de stock. Requiere login.
    """
    model = MovimientoStock
    form_class = MovimientoStock  # Formulario para crear movimientos de stock.
    template_name = 'stock/movimiento_form.html'  # Plantilla para el formulario de movimiento.

    def form_valid(self, form):
        """
        Guarda el movimiento y actualiza el stock del producto asociado.
        """
        movimiento = form.save(commit=False)
        movimiento.usuario = self.request.user  # Asigna el usuario actual al movimiento.

        producto = movimiento.producto

        if movimiento.tipo == 'ENTRADA':
            producto.stock_actual += movimiento.cantidad
            if movimiento.ubicacion_destino:
                producto.ubicacion = movimiento.ubicacion_destino

        elif movimiento.tipo == 'SALIDA':
            producto.stock_actual -= movimiento.cantidad

        elif movimiento.tipo == 'TRASPASO':
            producto.ubicacion = movimiento.ubicacion_destino

        producto.save()
        movimiento.save()

        messages.success(
            self.request,
            f"Movimiento registrado exitosamente. Stock actual: {producto.stock_actual}"
        )

        return redirect('stock:producto_detail', pk=producto.pk)

    def get_context_data(self, **kwargs):
        """
        No se añaden datos adicionales específicos para esta vista en el contexto.
        """
        context = super().get_context_data(**kwargs)
        return context


class ReporteErrorView(FormView):
    """
    Vista para que los usuarios reporten errores. No requiere login.
    """
    template_name = 'stock/reportar_error.html'  # Plantilla para el formulario de reporte de error.
    form_class = ReporteErrorForm  # Formulario para reportar errores.
    success_url = reverse_lazy('stock:reportar_error')  # URL a la que se redirige tras el envío exitoso.

    def form_valid(self, form):
        """
        Procesa el formulario válido (aquí se podría enviar un correo, guardar en BD, etc.).
        """
        # Aquí podrías guardar o enviar el error
        print("Reporte enviado:")
        print(form.cleaned_data)

        messages.success(self.request, "Gracias por reportar el error. Nuestro equipo lo revisará pronto.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Muestra un mensaje de error si el formulario no es válido.
        """
        messages.error(self.request, "Hay errores en el formulario. Por favor revísalo.")
        return super().form_invalid(form)


class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Vista para eliminar un producto. Requiere login y muestra una confirmación.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol not in ['admin', 'ventas']:
            return render(request, 'stock/403.html',
                          {'message': "No tienes permisos para acceder a esta página."},
                          status=403)
        return super().dispatch(request, *args, **kwargs)

    permission_required = 'control.delete_producto'
    model = Producto
    template_name = 'stock/producto_delete.html'  # Plantilla para confirmar la eliminación.
    success_url = reverse_lazy('stock:producto_list')  # URL a la que se redirige tras la eliminación.

    def delete(self, request, *args, **kwargs):
        """
        Sobrescribe el método delete para mostrar un mensaje de éxito.
        """
        messages.success(self.request, 'Producto eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


class CategoriaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Vista para eliminar una categoría. Requiere login y muestra una confirmación.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol not in ['admin', 'gestor']:
            return render(request, 'stock/403.html',
                          {'message': "No tienes permisos para acceder a esta página."},
                          status=403)
        return super().dispatch(request, *args, **kwargs)

    permission_required = 'control.delete_categoria'
    model = Categoria
    template_name = 'stock/categoria_delete.html'  # Plantilla para confirmar la eliminación.
    success_url = reverse_lazy('stock:categoria_list')  # URL a la que se redirige tras la eliminación.

    def delete(self, request, *args, **kwargs):
        """
        Sobrescribe el método delete para mostrar un mensaje de éxito.
        """
        # Añadir mensaje de éxito
        messages.success(self.request, 'Categoría eliminada correctamente.')
        return super().delete(request, *args, **kwargs)


class CategoriaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Vista para listar todas las categorías. No requiere login.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol not in ['admin', 'gestor']:
            return render(request, 'stock/403.html',
                          {'message': "No tienes permisos para acceder a esta página."},
                          status=403)
        return super().dispatch(request, *args, **kwargs)

    permission_required = 'control.view_categoria'
    model = Categoria
    template_name = 'stock/categoria_list.html'  # Plantilla para mostrar la lista de categorías.
    context_object_name = 'categorias'  # Nombre de la variable de las categorías en el contexto.


class CategoriaCreateView(CreateView, PermissionRequiredMixin, LoginRequiredMixin):
    """
    Vista para crear una nueva categoría. No requiere login.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol not in ['admin', 'gestor']:
            return render(request, 'stock/403.html',
                          {'message': "No tienes permisos para acceder a esta página."},
                          status=403)
        return super().dispatch(request, *args, **kwargs)

    permission_required = 'control.add_categoria'
    model = Categoria
    fields = ['nombre', 'color']  # Campos del formulario para crear una categoría.
    template_name = 'stock/categoria_create.html'  # Plantilla para la creación de categorías.
    success_url = reverse_lazy('stock:categoria_list')  # URL a la que se redirige tras la creación.


class CategoriaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Vista para editar una categoría existente. Requiere login.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol not in ['admin', 'gestor']:
            return render(request, 'stock/403.html',
                          {'message': "No tienes permisos para acceder a esta página."},
                          status=403)
        return super().dispatch(request, *args, **kwargs)

    permission_required = 'control.change_categoria'
    model = Categoria
    fields = ['nombre', 'color']  # Campos del formulario para editar una categoría.
    template_name = 'stock/categoria_edit.html'  # Plantilla para la edición de categorías.
    context_object_name = 'categoria'  # Nombre de la variable de la categoría en el contexto.

    # Después de actualizar, redirigimos al usuario a la lista de categorías
    success_url = reverse_lazy('stock:categoria_list')

    def form_valid(self, form):
        """
        Muestra un mensaje de éxito tras la actualización.
        """
        messages.success(self.request, 'Categoría actualizada correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Muestra un mensaje de error si el formulario no es válido.
        """
        messages.error(self.request, 'Hubo un error al actualizar la categoría.')
        return super().form_invalid(form)


class ProductoAPIView(APIView):
    def get(self, request):
        codigo = request.GET.get('codigo_barras')
        try:
            producto = Producto.objects.get(codigo_barras=codigo)
            return Response({
                'exists': True,
                'nombre': producto.nombre,
                'precio_compra': producto.precio_compra,
                'precio_venta': producto.precio_venta,
                'stock_actual': producto.stock_actual
            })
        except Producto.DoesNotExist:
            return Response({'exists': False})