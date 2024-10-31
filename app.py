from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# 200: La acción solicitada fue exitosa.
# 201: Se creo un nuevo recurso.
# 400: Solicitud mal formada.
# 404: No se encontró el recurso solicitado.

productos = [
    {"producto_id": 1, "nombre": "Camisa", "stock": 25},
    {"producto_id": 2, "nombre": "Pantalon", "stock": 7},
    {"producto_id": 3, "nombre": "Zapatos", "stock": 15},
    {"producto_id": 4, "nombre": "Sombrero", "stock": 5},
    {"producto_id": 5, "nombre": "Chaqueta", "stock": 8},
    {"producto_id": 6, "nombre": "Bufanda", "stock": 12},
    {"producto_id": 7, "nombre": "Guantes", "stock": 6},
    {"producto_id": 8, "nombre": "Calcetines", "stock": 9},
    {"producto_id": 9, "nombre": "Gorra", "stock": 4},
    {"producto_id": 10, "nombre": "Cinturon", "stock": 11},
    {"producto_id": 11, "nombre": "Gafas de sol", "stock": 7},
    {"producto_id": 12, "nombre": "Reloj", "stock": 3},
    {"producto_id": 13, "nombre": "Mochila", "stock": 6},
    {"producto_id": 14, "nombre": "Billetera", "stock": 10},
    {"producto_id": 15, "nombre": "Anillo", "stock": 2},
    {"producto_id": 16, "nombre": "Collar", "stock": 5},
    {"producto_id": 17, "nombre": "Pulsera", "stock": 8},
]

carritos = {}
seguimientos = {}
MAX_CARRITO_ITEMS = 15
MAX_OPERACIONES_CARRITO = 20
MAX_TIEMPO_INACTIVIDAD = timedelta(minutes = 5)
MAX_CANTIDAD_PRODUCTO = 10

def validar_carrito(carrito):
    # Que el carrito no tenga más de 15 ítems
    if len(carrito["items"]) > MAX_CARRITO_ITEMS:
        return False, "El carrito tiene más de 15 ítems"

    # Que no se hayan realizado más de 20 operaciones
    if carrito["operaciones"] > MAX_OPERACIONES_CARRITO:
        eliminar_carrito(carrito['carrito_id'])
        return False, "Se ha realizado mas de 20 operaciones - ¡Carrito eliminado!"

    # Que no haya más de 10 unidades de un mismo producto
    producto_cantidad = {}
    for item in carrito["items"]:
        producto_id, cantidad = item
        producto_cantidad[producto_id] = producto_cantidad.get(producto_id, 0) + cantidad
        if producto_cantidad[producto_id] > MAX_CANTIDAD_PRODUCTO:
            return False, "Hay más de 10 unidades de un mismo producto"

    # El stock de los productos para el carrito
    for item in carrito["items"]:
        producto_id, cantidad = item
        producto = next((p for p in productos if p["producto_id"] == producto_id), None)
        if not producto or cantidad > producto["stock"]:
            return False, "Stock insuficiente del producto"

    if (datetime.now() - carrito["ultima_modificacion"]) > MAX_TIEMPO_INACTIVIDAD:
        eliminar_carrito(carrito['carrito_id'])
        return False, "Tiempo de inactividad excedido - ¡Carrito eliminado!"

    return True, ""

def eliminar_carrito(carrito_id):
    if carrito_id in carritos:
        del carritos[carrito_id]

def actualizar_stock(producto_id, cantidad):
    producto = next((prod for prod in productos if prod["producto_id"] == producto_id), None)
    if producto:
        producto["stock"] -= cantidad

@app.get('/productos')
def get_productos():
    return jsonify(productos)

@app.get('/carritos')
def get_all_carrito():
    return jsonify(carritos)


@app.get('/carritos/<int:carrito_id>')
def get_carrito(carrito_id):
    if carrito_id in carritos:
        carrito_valido, mensaje = validar_carrito(carritos[carrito_id])
        if carrito_valido:
            carrito = carritos[carrito_id]
            carrito["operaciones"] += 1
            carrito["ultima_modificacion"] = datetime.now()
            return jsonify(carrito)  # Ver el diccionario
        return jsonify({"error": mensaje}), 400
    else:
        return jsonify({"error": 'Carrito no encontrado'}), 404

@app.post('/carritos')
def crear_carrito():
    user_id = request.args.get('user_id')  # Verifica si se agrego un parametro

    if not user_id:
        return jsonify({"error": "Se requiere el parametro 'user_id'"}), 400

    if user_id in carritos:
        return jsonify({"error": "Ya existe un carrito para este usuario"}), 400

    for carrito_id, carrito in carritos.items():
        if carrito["user_id"] == user_id:
            return jsonify({"error": "Ya existe un carrito para este usuario"}), 400

    carrito_id = len(carritos) + 1
    carrito = {
        "user_id": user_id,
        "carrito_id": carrito_id,
        "items": [],
        "operaciones": 0,
        "ultima_modificacion": datetime.now()
    }
    carritos[carrito_id] = carrito
    return jsonify(carrito), 201

@app.patch('/carritos/<int:carrito_id>')
def agregar_items_carrito(carrito_id):
    if carrito_id in carritos:
        carrito = carritos[carrito_id]
        productos_param = request.json.get('productos')  # Obtener datos JSON del cuerpo de la solicitud
        if productos_param:
            if isinstance(productos_param, list):
                for item in productos_param:
                    producto_id, cantidad = item

                    carrito_valido, mensaje = validar_carrito(carrito)
                    if carrito_valido:
                        carrito["items"].append((producto_id, cantidad))
                        carrito["operaciones"] +=1
                        actualizar_stock(producto_id, cantidad)
                        carrito["ultima_modificacion"] = datetime.now()
                    else:
                        return jsonify({"error": mensaje}), 400
                return jsonify(carrito)
            else:
                return jsonify({"error": "La lista de productos debe estar en formato de lista"}), 400
    return jsonify({"error": "Carrito no encontrado"}), 404


@app.put('/carritos/<int:carrito_id>')
def sobrescribir_carrito(carrito_id):
    if carrito_id in carritos:
        carrito = carritos[carrito_id]
        carrito["items"] = []
        carrito["operaciones"] = 0
        carrito["ultima_modificacion"] = datetime.now()
        return jsonify(carrito)
    return jsonify({"error": "Carrito no encontrado"}), 404

@app.delete('/carritos/<int:carrito_id>')
def quitar_carrito(carrito_id):
    if carrito_id in carritos:
        del carritos[carrito_id]
        return jsonify({"Aviso": "Carrito eliminado"})
    return jsonify({"error": "Carrito no encontrado"}), 404

@app.get('/pago/<int:carrito_id>')
def generar_pago(carrito_id):
    if carrito_id in carritos:
        carrito = carritos[carrito_id]
        carrito_valido, mensaje = validar_carrito(carrito)
        if not carrito_valido:
            return jsonify({"error": mensaje}), 400
        seguimiento_id = len(seguimientos) + 1
        seguimientos[seguimiento_id] = carrito
        del carritos[carrito_id]
        return jsonify({"seguimiento_id": seguimiento_id}), 200

    return jsonify({"error": "Carrito no encontrado"}), 404
