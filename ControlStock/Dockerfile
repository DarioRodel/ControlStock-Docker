# Imagen base
FROM python:3.13.2

# Establecer directorio de trabajo
WORKDIR /ControlStock

# Copiar todo el proyecto
COPY . /ControlStock
# Copiar el entrypoint personalizado
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Añadir wait-for-it.sh al contenedor
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh

# Dar permisos de ejecución al script
RUN chmod +x /wait-for-it.sh

# Exponer el puerto de Django
EXPOSE 8005

# Comando de arranque: esperar a que MySQL esté disponible y luego iniciar Django
CMD ["/entrypoint.sh"]
