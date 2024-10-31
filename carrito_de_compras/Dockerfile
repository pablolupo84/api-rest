#Utilizo una imagen base de Python 3.12

FROM python:3.12-slim
LABEL description = "Imagen de carrito_de_compras"

#Asigno como directorio de trabajo /app
WORKDIR /app/carrito_de_compras

COPY ./carrito_de_compras /app/carrito_de_compras/

RUN pip install --no-cache-dir -r /app/carrito_de_compras/requirements.txt

RUN mkdir -p /app/logs

EXPOSE 8000

#CMD ["uvicorn", "main_carrito:app", "--reload" ,"--host", "0.0.0.0", "--port", "8000"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]

