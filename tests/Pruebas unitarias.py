import unittest
from datetime import datetime, timedelta
import json
from app import app, productos, carritos

class TestMethods(unittest.TestCase):

    def setUp(self):

        '''test_client(): Realiza solicitudes directamente a la aplicación dentro del entorno de prueba
        sin la necesidad de un servidor HTTP externo. Esto permite simular solicitudes HTTP y verificar las
        respuestas sin ejecutar un servidor real.
        En el entorno de prueba, las solicitudes y respuestas se gestionan internamente, lo que facilita la
        escritura y ejecución de pruebas unitarias.
        No se abre ningún puerto real al usar test_client()
        '''
        self.app = app.test_client()
        self.app.testing = True
        # self.app.debug = True
        carritos.clear()

    def test_Obtener_productos_iniciales_igual_a_17(self):
        response = self.app.get(path='/productos')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 17)

    def test_al_iniciar_no_hay_carros_asignados(self):
        response = self.app.get(path=f'/carritos')
        data = json.loads(response.get_data())
        self.assertEqual(len(data),0)

    def test_agregar_un_carrito_con_user_id_237(self):
        user_id = 237
        response = self.app.post(path=f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['user_id'], str(237))

    '''
    def test_obtener_el_carrito_id_1(self):
        carrito_id = 1     
        response = self.app.get(path=f'/carritos/{carrito_id}')
        data = json.loads(response.get_data())
        self.assertEqual(data['carrito_id'], 1) 
    '''

    def test_agregar_1_item_un_carrito(self):
        user_id = 265
        response = self.app.post(path=f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())
        carrito_id = data["carrito_id"]

        producto = {
                    "productos": [[1,5],[5,4]]
                    }

        response_patch = self.app.patch(f'/carritos/{carrito_id}', data=json.dumps(producto), content_type='application/json')
        response=self.app.get(path=f'/carritos/{carrito_id}')
        data = json.loads(response.get_data())
        self.assertEqual(response_patch.status_code, 200)

    def test_agregar_item_que_supere_stock(self):
        user_id = 325
        response = self.app.post(path=f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())
        carrito_id = data["carrito_id"]

        producto = {
                    "productos": [[1,55],[5,4]]
                    }

        response_patch = self.app.patch(f'/carritos/{carrito_id}', data=json.dumps(producto), content_type='application/json')
        response=self.app.get(path=f'/carritos/{carrito_id}')
        data = json.loads(response.get_data())
        self.assertEqual(response_patch.status_code, 400)

    def test_agregar_mas_de_15_item_al_carrito(self):
        user_id = 377
        response = self.app.post(path=f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())
        carrito_id = data["carrito_id"]

        producto = {
                    "productos": [[1,2],[2,1],[3,1],[4,2],[5,2],[7,2],
                                    [8,2],[9,1],[10,1],[11,2],[12,2],[13,2],
                                    [14,2],[15,1],[16,1],[17,2]]
                    }

        response_patch = self.app.patch(f'/carritos/{carrito_id}', data=json.dumps(producto), content_type='application/json')
        response=self.app.get(path=f'/carritos/{carrito_id}')
        data = json.loads(response.get_data())
        self.assertEqual(response_patch.status_code, 400)

    def test_carro_con_mas_de_20_operaciones(self):
        user_id = 366
        response = self.app.post(path=f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())

        carrito_id = data["carrito_id"]

        for _ in range(21):
            producto = {
                "productos": [[1, 1]]
            }
            response = self.app.patch(f'/carritos/{carrito_id}', data=json.dumps(producto), content_type='application/json')

        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 400)


    def test_items_con_mismo_producto_id(self):
        user_id = 366

        response = self.app.post(f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())
        carrito_id = data["carrito_id"]
        self.assertEqual(response.status_code, 201)

        # Agrego sin exeder la cantidad maxima
        productos_lista = {"productos": [[2, 1], [2, 1]]}
        response = self.app.patch(f'/carritos/{carrito_id}', data=json.dumps(productos_lista), content_type='application/json')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 200)

        # Agredo superando la cantidad maxima
        productos_lista = {"productos": [[2, 7], [2, 5]]}
        response = self.app.patch(f'/carritos/{carrito_id}', data=json.dumps(productos_lista), content_type='application/json')
        data = json.loads(response.get_data())
        #print (data)
        self.assertEqual(response.status_code, 400)

    def test_inactividad_elimina_carrito(self):
        user_id = 111

        response = self.app.post(f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())
        carrito_id = data["carrito_id"]
        self.assertEqual(response.status_code, 201)

        # cargo una inactividad mayor a 100 minutos
        carritos[carrito_id]['ultima_modificacion'] = datetime.now() - timedelta(minutes=100)

        # Realizar un pago después de la inactividad'
        response = self.app.get(f'/pago/{carrito_id}')
        self.assertEqual(response.status_code, 400)

    def test_inactividad_al_ver_carrito(self):
        user_id = 126

        # Crear un nuevo carrito
        response = self.app.post(f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())
        carrito_id = data["carrito_id"]
        self.assertEqual(response.status_code, 201)

        carritos[carrito_id]['ultima_modificacion'] = datetime.now() - timedelta(minutes=100)
        response = self.app.get(f'/carritos/{carrito_id}')
        self.assertEqual(response.status_code, 400)

    def test_items_no_exceden_stock(self):
        user_id = 666

        response = self.app.post(f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())
        carrito_id = data["carrito_id"]
        self.assertEqual(response.status_code, 201)

        # Agregar ítems que exceden el stock
        productos_lista = {"productos": [[2, 1], [3, 25]]}

        response = self.app.patch(f'/carritos/{carrito_id}', data=json.dumps(productos_lista), content_type='application/json')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 400)


    def test_no_dos_carritos_simultaneos_para_mismo_usuario(self):
        user_id = 121

        response1 = self.app.post(f'/carritos?user_id={user_id}')
        data = json.loads(response1.get_data())
        carrito_id = data["carrito_id"]
        self.assertEqual(response1.status_code, 201)

        # Intentar crear otro carrito para el mismo usuario
        response2 = self.app.post(f'/carritos?user_id={user_id}')
        self.assertEqual(response2.status_code, 400)

        # Elimino el carrito
        response_delete = self.app.delete(f'/carritos/{carrito_id}')
        self.assertEqual(response_delete.status_code, 200)

        # CreO un nuevo carrito después de eliminar el anterior
        response3 = self.app.post(f'/carritos?user_id={user_id}')
        self.assertEqual(response3.status_code, 201)

    def test_stock_se_decrementa_despues_del_pago(self):
        user_id = 125

        response = self.app.post(f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())
        carrito_id = data["carrito_id"]
        self.assertEqual(response.status_code, 201)

        # Agrego items al carrito
        productos_lista = {"productos": [[3, 5], [4, 3]]}
        response = self.app.patch(f'/carritos/{carrito_id}', data=json.dumps(productos_lista),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_stock_antes_y_despues_de_las_operaciones(self):
        user_id = 125

        # Obtener el stock antes de agregar productos al carrito
        producto_3_stock_antes = next((p['stock'] for p in productos if p['producto_id'] == 3), None)
        producto_4_stock_antes = next((p['stock'] for p in productos if p['producto_id'] == 4), None)

        # Crear un nuevo carrito
        response = self.app.post(f'/carritos?user_id={user_id}')
        data = json.loads(response.get_data())
        carrito_id = data["carrito_id"]
        self.assertEqual(response.status_code, 201)

        # Agregar items al carrito
        productos_lista = {"productos": [[3, 5], [4, 3]]}
        response = self.app.patch(f'/carritos/{carrito_id}', data=json.dumps(productos_lista),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Obtener el stock después de agregar productos al carrito
        producto_3_stock_despues = next((p['stock'] for p in productos if p['producto_id'] == 3), None)
        producto_4_stock_despues = next((p['stock'] for p in productos if p['producto_id'] == 4), None)

        self.assertGreaterEqual(producto_3_stock_antes, producto_3_stock_despues)
        self.assertGreaterEqual(producto_4_stock_antes, producto_4_stock_despues)


if __name__ == '__main__':
    unittest.main()
