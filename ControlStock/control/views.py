import json

import openpyxl
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect, render  # Importa la función redirect para redireccionar a otras URLs.
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView  # Importa vistas genéricas de Django.
from django.urls import reverse_lazy  # Importa reverse_lazy para generar URLs de forma diferida.
from django.contrib import messages  # Importa el sistema de mensajes de Django para mostrar notificaciones al usuario.
from rest_framework.response import Response

from django import forms
from .forms import ProductoForm, ReporteErrorForm, ProductoAtributoFormSet, \
    MovimientoStockForm, ProductoAtributoBaseFormSet  # Importa los formularios de la aplicación.
from django.views.generic.edit import FormView  # Importa la vista genérica para manejar formularios.
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Producto, MovimientoStock, Categoria, Atributo, OpcionAtributo
from django.db.models import Sum, F
from django.views.generic import TemplateView
from rest_framework.views import APIView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils import timezone
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from django.forms import inlineformset_factory, modelformset_factory
from .models import Producto, ProductoAtributo
from .forms import ProductoForm, ProductoAtributoForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Atributo, OpcionAtributo  # Importa OpcionAtributo correctamente



class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'stock/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productos = Producto.objects.all()
        movimientos = MovimientoStock.objects.select_related('producto').order_by('-fecha')[:10]
        categorias = Categoria.objects.all()

        # Datos básicos
        context['movimientos'] = movimientos
        context['total_productos'] = productos.count()
        context['total_categorias'] = categorias.count()
        context['valor_inventario'] = productos.aggregate(
            total=Sum(F('precio_compra') * F('stock_actual'))
        )['total'] or 0
        context['productos_bajo_stock'] = productos.filter(stock_actual__lt=10)

        # Datos para gráficos
        categorias_data = []
        for categoria in categorias:
            total_stock = productos.filter(categoria=categoria).aggregate(
                total=Sum('stock_actual')
            )['total'] or 0
            categorias_data.append({
                'nombre': categoria.nombre,
                'total_stock': total_stock,
                'color': categoria.color or '#4F46E5'
            })

        context['categorias_nombres'] = json.dumps([c['nombre'] for c in categorias_data])
        context['categorias_stock'] = json.dumps([c['total_stock'] for c in categorias_data])
        context['categorias_colores'] = json.dumps([c['color'] for c in categorias_data])

        estados = dict(Producto.ESTADO_STOCK)
        estado_counts = {
            'NORMAL': productos.filter(estado='NORMAL').count(),
            'BAJO': productos.filter(estado='BAJO').count(),
            'AGOTADO': productos.filter(estado='AGOTADO').count(),
        }
        context['stock_estados_labels'] = json.dumps([estados['NORMAL'], estados['BAJO'], estados['AGOTADO']])
        context['stock_estados_data'] = json.dumps(
            [estado_counts['NORMAL'], estado_counts['BAJO'], estado_counts['AGOTADO']])
        context['stock_estados_colors'] = json.dumps(['#4CAF50', '#FF9800', '#F44336'])

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

    def form_valid(self, form):
        context = self.get_context_data()
        atributo_formset = context['atributo_formset']

        self.object = form.save()

        if atributo_formset.is_valid():
            instances = atributo_formset.save(commit=False)
            for instance in instances:
                instance.producto = self.object
                instance.save()
            for obj in atributo_formset.deleted_objects:
                if obj.pk:
                    obj.delete()

            # Registrar movimiento de entrada si el stock inicial es mayor a 0
            if self.object.stock_actual > 0:
                MovimientoStock.objects.create(
                    producto=self.object,
                    tipo='ENTRADA',
                    cantidad=self.object.stock_actual,
                    usuario=self.request.user
                )

            return super().form_valid(form)
        else:
            return self.form_invalid(form)


# Vistas para Productos
class ProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'control.view_producto'
    model = Producto
    template_name = 'stock/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if request.user.rol not in ['admin', 'ventas']:
            return render(request, 'stock/403.html',
                          {'message': "No tienes permisos para acceder a esta página."},
                          status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        categoria = self.request.GET.get('categoria')
        estado = self.request.GET.get('estado')
        atributo_id = self.request.GET.get('atributo')
        opciones_ids = self.request.GET.getlist('opcion')  # <-- Aquí

        if search:
            queryset = queryset.filter(
                Q(codigo_barras__icontains=search) |
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )
        if categoria:
            queryset = queryset.filter(categoria__id=categoria)
        if estado:
            queryset = queryset.filter(estado=estado)
        if atributo_id:
            queryset = queryset.filter(productoatributo__atributo_id=atributo_id)
        if opciones_ids:
            queryset = queryset.filter(productoatributo__opcion_id__in=opciones_ids)

        return queryset.select_related('categoria', 'ubicacion').prefetch_related(
            'productoatributo_set__atributo',
            'productoatributo_set__opcion'
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['estados'] = Producto.ESTADO_STOCK
        context['atributos'] = Atributo.objects.all()

        context['available_columns'] = [
            {'key': 'imagen', 'label': 'Imagen'},
            {'key': 'codigo', 'label': 'Código'},
            {'key': 'nombre', 'label': 'Nombre'},
            {'key': 'categoria', 'label': 'Categoría'},
            {'key': 'atributos', 'label': 'Atributos'},
            {'key': 'stock', 'label': 'Stock'},
            {'key': 'estado', 'label': 'Estado'},
            {'key': 'acciones', 'label': 'Acciones'},
        ]

        atributo_id = self.request.GET.get('atributo')
        if atributo_id:
            context['opciones'] = OpcionAtributo.objects.filter(atributo_id=atributo_id)
        else:
            context['opciones'] = None

        # Aquí obtenemos opciones_ids de nuevo
        opciones_ids = self.request.GET.getlist('opcion')
        context['opciones_seleccionadas'] = opciones_ids

        return context


class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'control.add_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'stock/producto_create.html'
    success_url = reverse_lazy('stock:producto_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ProductoAtributoFormSet = inlineformset_factory(
            Producto,
            ProductoAtributo,
            form=ProductoAtributoForm,
            formset=ProductoAtributoBaseFormSet,
            extra=1,
            can_delete=True,
            min_num=0,
            validate_min=False,
            validate_max=False
        )

        if self.request.POST:
            context['atributo_formset'] = ProductoAtributoFormSet(
                self.request.POST,
                instance=self.object,
                prefix='productoatributo_set'
            )
            # Aquí ajustamos el queryset para cada subform del formset
            for subform in context['atributo_formset'].forms:
                atributo_id = subform.data.get(f'{subform.prefix}-atributo')
                if atributo_id:
                    subform.fields['opcion'].queryset = OpcionAtributo.objects.filter(atributo_id=atributo_id)
        else:
            context['atributo_formset'] = ProductoAtributoFormSet(
                instance=self.object,
                queryset=ProductoAtributo.objects.none(),
                prefix='productoatributo_set'
            )
            # Para el caso GET, normalmente no hay valores en data,
            # pero si quieres, podrías inicializar el queryset vacío o con algún valor predeterminado
            for subform in context['atributo_formset'].forms:
                subform.fields['opcion'].queryset = OpcionAtributo.objects.none()

        # Agregar datos necesarios para el template
        context['atributos'] = Atributo.objects.prefetch_related('opciones')
        context['atributo_opciones_dict'] = {
            atributo.id: [
                {
                    'id': opcion.id,
                    'valor': opcion.valor  # Ajusta "valor" si tu modelo tiene otro campo relevante
                }
                for opcion in atributo.opciones.all()
            ]
            for atributo in context['atributos']
        }
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        atributo_formset = context['atributo_formset']

        self.object = form.save()

        if atributo_formset.is_valid():
            instances = atributo_formset.save(commit=False)
            for instance in instances:
                instance.producto = self.object
                instance.save()
            for obj in atributo_formset.deleted_objects:
                if obj.pk:
                    obj.delete()

            # Registrar movimiento de entrada si el stock inicial es mayor a 0
            if self.object.stock_actual > 0:
                movimiento = MovimientoStock(
                    producto=self.object,
                    tipo='ENTRADA',
                    cantidad=self.object.stock_actual,
                    usuario=self.request.user
                )
                movimiento.save(modificar_stock=False)

            return super().form_valid(form)
        else:
            return self.form_invalid(form)

def registrar_movimiento(request):
    if request.method == 'POST':
        form = MovimientoStockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_movimientos')  # Cambia esto por tu URL correcta
    else:
        form = MovimientoStockForm()

    return render(request, 'stock/movimiento_form.html', {'form': form})


class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'control.change_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'stock/producto_create.html'
    success_url = reverse_lazy('stock:producto_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ProductoAtributoFormSet = inlineformset_factory(
            Producto,
            ProductoAtributo,
            form=ProductoAtributoForm,
            formset=ProductoAtributoBaseFormSet,
            extra=0,
            can_delete=True,
            min_num=0,
            validate_min=False,
            validate_max=False
        )

        if self.request.POST:
            context['atributo_formset'] = ProductoAtributoFormSet(
                self.request.POST,
                instance=self.object,
                prefix='productoatributo_set'
            )
            # Ajustar queryset para cada subform según atributo seleccionado
            for subform in context['atributo_formset'].forms:
                atributo_id = subform.data.get(f'{subform.prefix}-atributo')
                if atributo_id:
                    subform.fields['opcion'].queryset = OpcionAtributo.objects.filter(atributo_id=atributo_id)
        else:
            context['atributo_formset'] = ProductoAtributoFormSet(
                instance=self.object,
                prefix='productoatributo_set'
            )
            # En GET, iniciar queryset vacío para 'opcion' o podrías mantener el queryset real para mostrar opciones ya seleccionadas
            for subform in context['atributo_formset'].forms:
                if subform.instance.atributo_id:
                    subform.fields['opcion'].queryset = OpcionAtributo.objects.filter(atributo_id=subform.instance.atributo_id)
                else:
                    subform.fields['opcion'].queryset = OpcionAtributo.objects.none()

        # Agregar datos para el template (atributos y opciones)
        context['atributos'] = Atributo.objects.prefetch_related('opciones')
        context['atributo_opciones_dict'] = {
            atributo.id: [
                {
                    'id': opcion.id,
                    'valor': opcion.valor
                }
                for opcion in atributo.opciones.all()
            ]
            for atributo in context['atributos']
        }

        return context

    def form_valid(self, form):
        self.object = form.save()

        ProductoAtributoFormSet = inlineformset_factory(
            Producto,
            ProductoAtributo,
            form=ProductoAtributoForm,
            formset=ProductoAtributoBaseFormSet,
            extra=0,
            can_delete=True,
        )

        atributo_formset = ProductoAtributoFormSet(
            self.request.POST,
            instance=self.object,
            prefix='productoatributo_set'
        )

        # 💡 Asigna correctamente el queryset del campo 'opcion' según el 'atributo' enviado
        for subform in atributo_formset.forms:
            atributo_id = subform.data.get(f'{subform.prefix}-atributo')
            if atributo_id:
                try:
                    subform.fields['opcion'].queryset = OpcionAtributo.objects.filter(atributo_id=atributo_id)
                except (ValueError, TypeError):
                    subform.fields['opcion'].queryset = OpcionAtributo.objects.none()
            else:
                subform.fields['opcion'].queryset = OpcionAtributo.objects.none()

        if atributo_formset.is_valid():
            atributo_formset.save()
            return super().form_valid(form)
        else:
            context = self.get_context_data(form=form)
            context['atributo_formset'] = atributo_formset
            return self.render_to_response(context)


class MovimientoStockCreateView(LoginRequiredMixin, CreateView):
    model = MovimientoStock
    form_class = MovimientoStockForm  # Usa el formulario, no el modelo
    template_name = 'stock/movimiento_form.html'

    def form_valid(self, form):
        movimiento = form.save(commit=False)
        movimiento.usuario = self.request.user
        movimiento.save()  # Aquí se actualiza el stock automáticamente por el modelo
        messages.success(
            self.request,
            f"Movimiento registrado exitosamente. Stock actual: {movimiento.producto.stock_actual}"
        )
        return redirect('stock:producto_detail', pk=movimiento.producto.pk)


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


class ExportMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        # Aplicar los mismos filtros que en la vista principal
        search = self.request.GET.get('search')
        categoria = self.request.GET.get('categoria')
        estado = self.request.GET.get('estado')

        if search:
            queryset = queryset.filter(
                Q(codigo_barras__icontains=search) |
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )

        if categoria:
            queryset = queryset.filter(categoria__id=categoria)

        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset


def export_productos_csv(request):
    productos = Producto.objects.all()

    search = request.GET.get('search')
    categoria = request.GET.get('categoria')
    estado = request.GET.get('estado')

    if search:
        productos = productos.filter(
            Q(codigo_barras__icontains=search) |
            Q(nombre__icontains=search) |
            Q(descripcion__icontains=search)
        )

    if categoria:
        productos = productos.filter(categoria__id=categoria)

    if estado:
        productos = productos.filter(estado=estado)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="productos_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Código', 'Nombre', 'Categoría', 'Stock Actual', 'Precio Compra', 'Precio Venta', 'Estado'])

    for producto in productos:
        writer.writerow([
            producto.codigo_barras,
            producto.nombre,
            producto.categoria.nombre,
            producto.stock_actual,
            producto.precio_compra,
            producto.precio_venta,
            producto.get_estado_display()
        ])
    return response


def export_productos_excel(request):
    productos = Producto.objects.all()

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="productos_{timezone.now().date()}.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"

    # Encabezados
    columns = ['Código', 'Nombre', 'Categoría', 'Stock Actual', 'Precio Compra', 'Precio Venta', 'Estado']
    ws.append(columns)

    # Datos
    for producto in productos:
        ws.append([
            producto.codigo_barras,
            producto.nombre,
            producto.categoria.nombre,
            producto.stock_actual,
            producto.precio_compra,
            producto.precio_venta,
            producto.get_estado_display()
        ])

    wb.save(response)
    return response


def export_productos_pdf(request):
    productos = Producto.objects.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="productos_{timezone.now().date()}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Reporte de Productos")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, f"Fecha: {timezone.now().date()}")

    # Datos de la tabla
    data = [['Código', 'Nombre', 'Categoría', 'Stock', 'P. Compra', 'P. Venta', 'Estado']]

    for producto in productos:
        data.append([
            producto.codigo_barras,
            producto.nombre,
            producto.categoria.nombre,
            str(producto.stock_actual),
            f"€{producto.precio_compra}",
            f"€{producto.precio_venta}",
            producto.get_estado_display()
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    table.wrapOn(p, width - 100, height)
    table.drawOn(p, 50, height - 150)

    p.showPage()
    p.save()
    return response


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


class AtributoListView(LoginRequiredMixin, ListView):
    model = Atributo
    template_name = 'stock/atributo_list.html'


@csrf_exempt
@require_POST
def opcion_create_ajax(request):
    atributo_id = request.POST.get('atributo')
    valor = request.POST.get('valor')

    try:
        atributo = Atributo.objects.get(pk=atributo_id)
        opcion = OpcionAtributo.objects.create(
            atributo=atributo,
            valor=valor
        )
        return JsonResponse({
            'success': True,
            'opcion_id': opcion.id,
            'opcion_valor': opcion.valor
        })
    except Atributo.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Atributo no encontrado'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


class AtributoCreateView(LoginRequiredMixin, CreateView):
    model = Atributo
    fields = ['nombre', 'descripcion']
    template_name = 'stock/atributo_form.html'
    success_url = reverse_lazy('stock:atributo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['opcion_formset'] = self.OpcionFormSet(
                self.request.POST,
                instance=self.object if hasattr(self, 'object') else None,
                prefix='opcion_set'
            )
        else:
            context['opcion_formset'] = self.OpcionFormSet(
                instance=self.object if hasattr(self, 'object') else None,
                prefix='opcion_set'
            )

        return context

    @property
    def OpcionFormSet(self):
        return inlineformset_factory(
            Atributo,
            OpcionAtributo,
            fields=('valor', 'color'),
            extra=0,
            can_delete=True,
            widgets={
                'valor': forms.TextInput(attrs={'class': 'form-control'}),
                'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            }
        )

    def form_valid(self, form):
        context = self.get_context_data()
        opcion_formset = context['opcion_formset']

        if opcion_formset.is_valid():
            self.object = form.save()
            opcion_formset.instance = self.object
            opcion_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AtributoUpdateView(LoginRequiredMixin, UpdateView):
    model = Atributo
    fields = ['nombre', 'descripcion']
    template_name = 'stock/atributo_form.html'
    success_url = reverse_lazy('stock:atributo_list')  # ✅ ESTA LÍNEA ES CLAVE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['opcion_formset'] = self.OpcionFormSet(
                self.request.POST,
                instance=self.object,
                prefix='opcion_set'
            )
        else:
            context['opcion_formset'] = self.OpcionFormSet(
                instance=self.object,
                prefix='opcion_set'
            )
        return context

    @property
    def OpcionFormSet(self):
        return inlineformset_factory(
            Atributo,
            OpcionAtributo,
            fields=('valor','color'),
            extra=0,
            can_delete=True,
            widgets={
                'valor': forms.TextInput(attrs={'class': 'form-control'}),
                'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            }
        )

    def form_valid(self, form):
        context = self.get_context_data()
        opcion_formset = context['opcion_formset']

        if not opcion_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()
        opcion_formset.instance = self.object
        opcion_formset.save()

        return redirect(self.get_success_url())
# AtributoDeleteView ya está bien configurada, no se requieren cambios
class AtributoDeleteView(LoginRequiredMixin, DeleteView):
    model = Atributo
    template_name = 'stock/atributo_confirm_delete.html'
    success_url = reverse_lazy('stock:atributo_list')


class OpcionAtributoForm(forms.ModelForm):
    productos = forms.ModelMultipleChoiceField(
        queryset=Producto.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = OpcionAtributo
        fields = ['atributo', 'valor', 'orden', 'productos']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['productos'].initial = self.instance.productos.all()

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            instance.productos.set(self.cleaned_data['productos'])
        return instance


class OpcionAtributoCreateView(LoginRequiredMixin, CreateView):
    model = OpcionAtributo
    form_class = OpcionAtributoForm
    template_name = 'stock/opcionatributo_form.html'
    success_url = reverse_lazy('stock:atributo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all()  # Añade esto
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save_m2m()  # Necesario para guardar relaciones many-to-many
        return response
