from django.contrib.auth.views import LogoutView  # Vista incorporada de Django para cerrar sesión.
from django.urls import path  # Función para definir patrones de URL.
from . import views  # Importa todas las vistas desde el archivo views.py de la misma app.
from .views import (
    ProductoListView,
    ReporteErrorView,
    CategoriaCreateView,
    ProductoAPIView,
    CategoriaUpdateView, export_productos_csv, export_productos_excel, export_productos_pdf, AtributoListView,
    AtributoCreateView, AtributoUpdateView, AtributoDeleteView
)  # Importación directa de clases de vistas específicas, para mayor claridad o reutilización.
from django.conf import settings  # Permite acceder a configuraciones del proyecto (como DEBUG, MEDIA_URL, etc.).
from django.conf.urls.static import static  # Se usa para servir archivos estáticos/media durante el desarrollo.

# Namespace de la aplicación. Útil para usar 'stock:producto_list', por ejemplo, en los templates.
app_name = 'stock'

# Lista de patrones de URL que definen el enrutamiento de la app.
urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    # Ruta principal (/) que muestra el dashboard de la aplicación.

    path('productos/', ProductoListView.as_view(), name='producto_list'),
    # Muestra la lista de productos.

    path('productos/nuevo/', views.ProductoCreateView.as_view(), name='producto_create'),
    # Página/formulario para registrar un nuevo producto.

    path('productos/<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    # Muestra los detalles de un producto en base a su ID (pk = primary key).

    path('productos/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_edit'),
    # Página para editar un producto existente.

    path('productos/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_delete'),
    # Página o acción para eliminar un producto existente.

    path('reportar-error/', ReporteErrorView.as_view(), name='reportar_error'),
    # Ruta para que los usuarios puedan reportar errores o problemas.

    path('categorias/nueva/', CategoriaCreateView.as_view(), name='categoria_create'),
    # Página para crear una nueva categoría.

    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    # Lista de todas las categorías.

    path('categoria/<int:pk>/editar/', CategoriaUpdateView.as_view(), name='categoria_edit'),
    # Página para editar una categoría específica.

    path('categoria/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),
    # Página o acción para eliminar una categoría específica.

    path('api/productos/', ProductoAPIView.as_view(), name='producto-api'),
    # Ruta para la API de productos, devuelve datos en formato JSON.

    path('logout/', LogoutView.as_view(), name='logout'),
    # Ruta para cerrar sesión de usuario.

    path('productos/exportar/csv/', export_productos_csv, name='export_productos_csv'),
    path('productos/exportar/excel/', export_productos_excel, name='export_productos_excel'),
    path('productos/exportar/pdf/', export_productos_pdf, name='export_productos_pdf'),
    path('atributos/', AtributoListView.as_view(), name='atributo_list'),
    path('atributos/nuevo/', AtributoCreateView.as_view(), name='atributo_create'),
    path('atributo/editar/<int:pk>/', AtributoUpdateView.as_view(), name='atributo_update'),
    path('atributos/<int:pk>/eliminar/', AtributoDeleteView.as_view(), name='atributo_delete'),
    path('atributo/nuevo/', AtributoCreateView.as_view(), name='atributo_create'),
    path('atributo/editar/<int:pk>/', AtributoUpdateView.as_view(), name='atributo_update'),
    path('opciones/crear/ajax/', views.opcion_create_ajax, name='opcion_create_ajax'),
]

# Esta configuración solo aplica si el entorno está en modo desarrollo.
# Sirve archivos multimedia (como imágenes de productos o QR) desde MEDIA_ROOT cuando DEBUG=True.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
