from bson.objectid import ObjectId
from datetime import datetime
import hashlib


dateFormatStr = '%d-%m-%Y'


class Endoso:

    def __init__(self):
        self.id_anterior_endoso = "null"
        self.id_endosante = "null"
        self.nombre_endosante = "null"
        self.id_endosatario = "null"
        self.nombre_endosatario = "null"
        self.id_pagare = "null"
        self.fecha = "null"
        self.firma = "null"
        self.hash_transaccion = "null"
        self.confirmacion_transaccion = "null"
        self.codigo_retiro = "null"
        self.etapa = -1
        self.es_ultimo_endoso = False

    def endosoFromRequest(self, p_request, id_pagare, anterior_endoso):
        # self._id = p_request.json['_id']
        self.id_anterior_endoso = anterior_endoso
        self.id_endosante = p_request.json['id_endosante']
        self.nombre_endosante = p_request.json['nombre_endosante']
        self.id_endosatario = p_request.json['id_endosatario']
        self.nombre_endosatario = p_request.json['nombre_endosatario']
        self.id_pagare = id_pagare
        self.fecha = str(datetime.today())
        self.firma = p_request.json['firma']
        self.codigo_retiro = "null"
        self.etapa = 2
        

    def endosoFromDoc(self, doc):
        self._id = str(doc['_id'])
        self.id_anterior_endoso = doc['id_anterior_endoso']
        self.id_endosante = doc['id_endosante']
        self.nombre_endosante = doc['nombre_endosante']
        self.id_endosatario = doc['id_endosatario']
        self.nombre_endosatario = doc['nombre_endosatario']
        self.id_pagare = doc['id_pagare']
        self.fecha = doc['fecha']
        self.firma = doc['firma']
        self.hash_transaccion = doc['hash_transaccion']
        self.confirmacion_transaccion = doc['confirmacion_transaccion']
        self.etapa = doc['etapa']
        self.codigo_retiro = doc['codigo_retiro']
        self.es_ultimo_endoso = doc['es_ultimo_endoso']

    def setId(self, id):
        self._id = id

    def firmar(self):
        string = self._id + self.firma + self.id_anterior_endoso + \
            self.id_pagare + self.id_endosante + self.id_endosatario
        hash_object = hashlib.sha256((string.encode()))
        hex_dig = hash_object.hexdigest()
        print(hex_dig)
        self.firma = hex_dig
        return hex_dig

    def from_blockchain(self, bc_string):
        # self._id = bc_string[0]
        # self.id_anterior_endoso = bc_string[1]
        # self.id_endosante = bc_string[2].split(',')[0]
        # self.nombre_endosante = bc_string[2].split(',')[1]
        # self.id_endosatario = bc_string[3].split(',')[0]
        # self.nombre_endosatario = bc_string[3].split(',')[1]
        # self.id_pagare = bc_string[4]
        # self.fecha = bc_string[5]
        # self.firma = bc_string[6]
        return {
            "_id": bc_string[0],
            "id_anterior_endoso": bc_string[1],
            "info_endosante":bc_string[2],
            "info_endosatario":bc_string[3],
            "id_pagare":bc_string[4],
            "fecha":bc_string[5],
            "firma":bc_string[6]
        }


