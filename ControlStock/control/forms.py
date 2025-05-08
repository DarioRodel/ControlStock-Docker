from django import forms  # Importa el módulo de formularios de Django.
from .models import MovimientoStock, Producto, Ubicacion  # Importa los modelos relacionados con los formularios.


class MovimientoStockForm(forms.ModelForm):
    """
    Formulario para registrar movimientos de stock.
    Hereda de forms.ModelForm y está asociado al modelo MovimientoStock.
    """
    class Meta:
        model = MovimientoStock  # Especifica el modelo al que este formulario está asociado.
        fields = ['producto', 'tipo', 'cantidad', 'ubicacion_origen', 'ubicacion_destino', 'observaciones']  # Define los campos del modelo que se incluirán en el formulario.
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),  # Utiliza un widget Textarea para el campo de observaciones con 3 filas.
        }

    def __init__(self, *args, **kwargs):
        """
        Método de inicialización del formulario.
        Se utiliza para personalizar los campos del formulario.
        """
        super().__init__(*args, **kwargs)  # Llama al método __init__ de la clase padre.

        # Filtramos productos activos para el campo 'producto'
        self.fields['producto'].queryset = Producto.objects.filter(activo=True)

        # Filtramos todas las ubicaciones para los campos de origen y destino
        self.fields['ubicacion_origen'].queryset = Ubicacion.objects.all()
        self.fields['ubicacion_destino'].queryset = Ubicacion.objects.all()

        # Los campos de ubicación no son requeridos por defecto, se validan condicionalmente en el método clean.
        self.fields['ubicacion_origen'].required = False
        self.fields['ubicacion_destino'].required = False

        # Añadir la clase CSS 'form-control' a todos los campos del formulario para estilos de Bootstrap.
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        """
        Método para realizar validaciones personalizadas en los datos del formulario.
        Se llama después de la validación de los campos individuales.
        """
        cleaned_data = super().clean()  # Obtiene los datos limpios del formulario.
        tipo = cleaned_data.get('tipo')  # Obtiene el valor del campo 'tipo'.
        cantidad = cleaned_data.get('cantidad')  # Obtiene el valor del campo 'cantidad'.
        producto = cleaned_data.get('producto')  # Obtiene el objeto Producto seleccionado.
        ubicacion_origen = cleaned_data.get('ubicacion_origen')  # Obtiene la ubicación de origen.
        ubicacion_destino = cleaned_data.get('ubicacion_destino')  # Obtiene la ubicación de destino.

        # Validación específica para el tipo de movimiento 'SALIDA'
        if tipo == 'SALIDA':
            if producto and cantidad is not None and producto.stock_actual < cantidad:
                # Si la cantidad a dar de salida es mayor que el stock actual, levanta un error de validación.
                raise forms.ValidationError(
                    f"No hay suficiente stock. Stock actual: {producto.stock_actual}"
                )
            if not ubicacion_origen:
                # Si el tipo es 'SALIDA' y no se ha seleccionado una ubicación de origen, levanta un error.
                raise forms.ValidationError("Debe seleccionar una ubicación de origen para las salidas")

        # Validación específica para el tipo de movimiento 'TRASPASO'
        if tipo == 'TRASPASO':
            if not ubicacion_origen or not ubicacion_destino:
                # Si el tipo es 'TRASPASO' y falta alguna de las ubicaciones, levanta un error.
                raise forms.ValidationError("Debe seleccionar ambas ubicaciones para traspasos")
            if ubicacion_origen == ubicacion_destino:
                # Si las ubicaciones de origen y destino son la misma, levanta un error.
                raise forms.ValidationError("Las ubicaciones de origen y destino deben ser diferentes")

        return cleaned_data  # Devuelve los datos limpios, incluyendo las validaciones personalizadas.


class ProductoForm(forms.ModelForm):
    """
    Formulario para crear o editar productos.
    Incluye el campo 'estado' para manejar el estado del stock.
    """
    class Meta:
        model = Producto  # Asocia el formulario con el modelo Producto.
        fields = [ 'codigo_barras', 'nombre', 'categoria', 'ubicacion', 'descripcion',
                  'precio_compra', 'precio_venta', 'stock_actual', 'stock_minimo', 'estado', 'imagen']  # Asegúrate de incluir 'estado'.
        widgets = {
            'nombre': forms.TextInput(attrs={'required': True}),
            'codigo_barras': forms.TextInput(attrs={'required': True}),
            'categoria': forms.Select(attrs={'required': True}),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if Producto.objects.filter(codigo=codigo).exists():
            raise forms.ValidationError("Este código ya está en uso.")
        return codigo

class ReporteErrorForm(forms.Form):
    """
    Formulario para que los usuarios reporten errores o problemas.
    No está directamente asociado a un modelo de base de datos.
    """
    asunto = forms.CharField(label="Asunto", max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Título breve del error',
    }))  # Campo para el asunto del reporte, con un widget TextInput y atributos HTML.
    descripcion = forms.CharField(label="Descripción", widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Describe el error lo más detalladamente posible...',
        'rows': 5
    }))  # Campo para la descripción del error, con un widget Textarea y atributos HTML.
    email = forms.EmailField(label="Correo electrónico", required=False, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'tu@correo.com'
    }))  # Campo opcional para el correo electrónico del reportante, con un widget EmailInput y atributos HTML.