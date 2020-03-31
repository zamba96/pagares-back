from bson.objectid import ObjectId
from datetime import datetime
import hashlib


dateFormatStr = '%d-%m-%Y'

class Pagare:

    def __init__(self):
        self.valor = -1
        self.nombreDeudor = "null"
        self.idDeudor = "null"
        self.nombreAcreedor = "null"
        self.idAcreedor = "null"
        self.fechaCreacion = ""
        self.lugarCreacion = "null"
        self.fechaVencimiento = ""
        self.fechaExpiracion = ""
        self.lugarCumplimiento = "null"
        self.firma = "null"
        self.ultimoEndoso = "null"
        self.pendiente = False
        self.etapa = -1
        self.terminos = "null"
        self.codigoRetiro = "null"
        self.confirmacionRetiro = "null"


    def pagareFromRequest(self, p_request):
        self.valor = p_request.json['valor']
        self.nombreDeudor = p_request.json['nombreDeudor']
        self.idDeudor = p_request.json['idDeudor']
        self.nombreAcreedor = p_request.json['nombreAcreedor']
        self.idAcreedor = p_request.json['idAcreedor']
        self.fechaCreacion = datetime.strptime(p_request.json['fechaCreacion'], dateFormatStr)
        self.lugarCreacion = p_request.json['lugarCreacion']
        self.fechaVencimiento = datetime.strptime(p_request.json['fechaVencimiento'], dateFormatStr)
        self.fechaExpiracion = datetime.strptime(p_request.json['fechaExpiracion'], dateFormatStr)
        self.lugarCumplimiento = p_request.json['lugarCumplimiento']
        self.firma = "null"


    def pagareFromDoc(self, doc):
        self.valor = doc['valor']
        self.nombreDeudor = doc['nombreDeudor']
        self.idDeudor = doc['idDeudor']
        self.nombreAcreedor = doc['nombreAcreedor']
        self.idAcreedor = doc['idAcreedor']
        self.fechaCreacion = doc['fechaCreacion']
        self.lugarCreacion = doc['lugarCreacion']
        self.fechaVencimiento = doc['fechaVencimiento']
        self.fechaExpiracion = doc['fechaExpiracion']
        self.lugarCumplimiento = doc['lugarCumplimiento']
        self.firma = doc['firma']
        self._id = str(doc['_id'])
        self.ultimoEndoso = doc['ultimoEndoso']
        self.pendiente = doc['pendiente']
        self.etapa = doc['etapa']
        self.terminos = doc['terminos']
        self.codigoRetiro = doc['codigoRetiro']
        self.confirmacionRetiro = doc['confirmacionRetiro']

    def setId(self, id):
        self._id = id

    def firmar(self):
        string = self._id + str(self.valor) + self.nombreDeudor + str(self.idDeudor) + self.nombreAcreedor + str(self.idAcreedor)
        hash_object = hashlib.sha256((string.encode()))
        hex_dig = hash_object.hexdigest()
        print(hex_dig)
        self.firma = hex_dig
        return hex_dig


class PagareBlockChain:

    def __init__(self, pagare_string):
        self._id = pagare_string[0]
        self.valor  = pagare_string[1]
        self.id_deudor = pagare_string[2]
        self.id_acreedor = pagare_string[3]
        self.info = pagare_string[4]
        self.pendiente = pagare_string[5]
        self.ultimo_endoso = pagare_string[6]