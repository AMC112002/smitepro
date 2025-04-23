# Usa una imagen oficial de Python como base
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . /app

# Instala dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto
EXPOSE 8000

# Comando por defecto: migra, recoge estáticos y lanza el servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn smitepro.wsgi:application --bind 0.0.0.0:8000"]
