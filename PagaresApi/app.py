from flask import Flask
from pymongo import MongoClient
from flask import jsonify
from flask import request
from bson.objectid import ObjectId
from datetime import datetime
from datetime import timedelta
import hashlib
from blockChainAccess import BlockChainAccess
from Pagare import Pagare

dateFormatStr = '%d-%m-%Y'

client = MongoClient(
    "mongodb+srv://admin:adminPass@cluster0-e8ksn.mongodb.net/test?retryWrites=true&w=majority")
db = client.tesis

app = Flask(__name__)
bca = BlockChainAccess()

@app.route('/')
def hello_world():
    return "Welcome to the Mock Blockchain API"


# Route: /pagares

# POST
# Crea un nuevo pagare, retorna el nuevo pagare
@app.route('/pagares', methods=['POST'])
def createPagare():
    pagare = Pagare()

    pagare.pagareFromRequest(request)
    id = db.pagares.insert_one(vars(pagare)).inserted_id
    pagareRetorno = Pagare()
    docPagare = db.pagares.find_one({"_id": ObjectId(str(id))})
    pagareRetorno.pagareFromDoc(docPagare)
    pagareRetorno.firmar()
    print(pagareRetorno)
    db.pagares.update_one({"_id": ObjectId(str(id))}, {
                          '$set': {"firma": pagareRetorno.firma}})
    print(vars(pagareRetorno))
    return vars(pagareRetorno)


# GET
# Trae la lista de pagares
@app.route('/pagares', methods=['GET'])
def getPagare():
    pagares = db.pagares.find()
    pagaresList = list(pagares)
    returnList = []
    for p in pagaresList:
        pagare = Pagare()
        pagare.pagareFromDoc(p)
        returnList.append(vars(pagare))
    return jsonify(returnList)


# Route /pagares/<idPagare>
# GET
@app.route('/pagares/<id_pagare>', methods=['GET'])
def getPagareById(id_pagare):
    try:
        pagareDoc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if pagareDoc == None:
        return "Pagare no encontrado", 404
    pagare = Pagare()
    pagare.pagareFromDoc(pagareDoc)
    return vars(pagare)


# route /pagares/etapa1/
# PUT 
# Crea un nuevo pagare en etapa 1
@app.route('/pagares/etapa1', methods=['POST'])
def crear_pagare_1():
    pagare = Pagare()
    pagare.idAcreedor = request.json['idAcreedor']
    pagare.idDeudor = request.json['idDeudor']
    pagare.nombreAcreedor = request.json['nombreAcreedor']
    pagare.nombreDeudor = request.json['nombreDeudor']
    pagare.etapa = 1
    _id = db.pagares.insert_one(vars(pagare)).inserted_id
    pagare = Pagare()
    doc = db.pagares.find_one({'_id':_id})
    pagare.pagareFromDoc(doc)
    return vars(pagare)




# route /pagares/<id_pagare>/etapa2
# PUT 
# Crea un nuevo pagare en etapa 2
@app.route('/pagares/<id_pagare>/etapa2', methods=['PUT'])
def crear_pagare_2(id_pagare):
    
    try:
        doc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Pagare no encontrado", 404

    pagare = Pagare()
    pagare.pagareFromDoc(doc)
    pagare.valor = request.json['valor']
    pagare.terminos = request.json['terminos']
    pagare.acreedorAcepta = request.json['acreedorAcepta']
    pagare.deudorAcepta = request.json['deudorAcepta']
    pagare.etapa = 2

    updates = getUpdateStatement(pagare)

    db.pagares.update_one({'_id':ObjectId(id_pagare)}, {'$set': updates})
    doc = db.pagares.find_one({'_id':ObjectId(id_pagare)})
    pagare.pagareFromDoc(doc)
    return vars(pagare)


# Route /pagares/<id_pagare>/etapa2/aceptar
# PUT
# Acepta el pagare
@app.route('/pagares/<id_pagare>/etapa2/aceptar')
def aceptar_pagare(id_pagare):
    try:
        doc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Pagare no encontrado", 404

    pagare = Pagare()
    pagare.pagareFromDoc(doc)
    pagare.acreedorAcepta = request.json['acreedorAcepta']
    pagare.deudorAcepta = request.json['deudorAcepta']
    pagare.etapa = 2

    updates = getUpdateStatement(pagare)

    db.pagares.update_one({'_id':ObjectId(id_pagare)}, {'$set': updates})
    doc = db.pagares.find_one({'_id':ObjectId(id_pagare)})
    pagare.pagareFromDoc(doc)
    return vars(pagare)

# route /pagares/<id_pagare>/etapa3
# PUT
# Crea un nuevo pagare en etapa 3
@app.route('/pagares/<id_pagare>/etapa3', methods=['PUT'])
def crear_pagare_3(id_pagare):
    
    try:
        doc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Pagare no encontrado", 404

    pagare = Pagare()
    pagare.pagareFromDoc(doc)
    pagare.fechaVencimiento = datetime.strptime(request.json['fechaVencimiento'], dateFormatStr)
    pagare.lugarCreacion = request.json['lugarCreacion']
    pagare.lugarCumplimiento = request.json['lugarCumplimiento']
    pagare.codigoRetiro = request.json['codigoRetiro']
    pagare.etapa = 3

    updates = getUpdateStatement(pagare)

    db.pagares.update_one({'_id':ObjectId(id_pagare)}, {'$set': updates})
    doc = db.pagares.find_one({'_id':ObjectId(id_pagare)})
    pagare.pagareFromDoc(doc)
    return vars(pagare)


# route /pagares/<id_pagare>/etapa4
# PUT
# Crea un nuevo pagare en etapa 4
@app.route('/pagares/<id_pagare>/etapa4', methods=['PUT'])
def crear_pagare_4(id_pagare):
    
    try:
        doc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Pagare no encontrado", 404

    pagare = Pagare()
    pagare.pagareFromDoc(doc)
    pagare.firma = request.json['firma']
    fecha_hoy = datetime.today()
    fecha_expr = datetime.now() + timedelta(days=5*365)
    pagare.etapa = 4
    pagare.pendiente = True
    pagare.fechaCreacion = fecha_hoy
    pagare.fechaExpiracion = fecha_expr
    hash_transaccion = bca.crear_pagare(pagare)
    pagare.hash_transaccion = hash_transaccion
    updates = getUpdateStatement(pagare)

    db.pagares.update_one({'_id':ObjectId(id_pagare)}, {'$set': updates})
    doc = db.pagares.find_one({'_id':ObjectId(id_pagare)})
    pagare.pagareFromDoc(doc)
    return vars(pagare)


# Route /pagares/<id_pagare>/blockchain
# GET
# Retorna la informacion plana que esta en el blockchain sobre el pagare
@app.route('/pagares/<id_pagare>/blockchain', methods=['GET'])
def get_pagare_blockchain(id_pagare):
    return bca.get_pure_pagare(id_pagare)


# Route /pagares/deudor/<idDeudor>
# GET
# Trae la lista de pagares del deudor id_deudor
@app.route('/pagares/deudor/<id_deudor>', methods=['GET'])
def getPagaresDeudor(id_deudor):
    pagares = db.pagares.find({'idDeudor':int(id_deudor) })
    pagaresList = list(pagares)
    returnList = []
    for p in pagaresList:
        pagare = Pagare()
        pagare.pagareFromDoc(p)
        returnList.append(vars(pagare))
    return jsonify(returnList)


# Route /pagares/acreedor/<id_acreedor>
# GET
# Trae la lista de pagares del acreedor id_acreedor
@app.route('/pagares/acreedor/<id_acreedor>', methods=['GET'])
def getPagaresAcreedor(id_acreedor):
    pagares = db.pagares.find({'idAcreedor':int(id_acreedor)})
    pagaresList = list(pagares)
    returnList = []
    for p in pagaresList:
        pagare = Pagare()
        pagare.pagareFromDoc(p)
        returnList.append(vars(pagare))
    return jsonify(returnList)



def getUpdateStatement(pagare: Pagare):
    return {
        'valor':pagare.valor,
        'nombreDeudor':pagare.nombreDeudor,
        'idDeudor':pagare.idDeudor,
        'nombreAcreedor':pagare.nombreAcreedor,
        'idAcreedor':pagare.idAcreedor,
        'fechaCreacion':pagare.fechaCreacion,
        'lugarCreacion':pagare.lugarCreacion,
        'fechaVencimiento':pagare.fechaVencimiento,
        'fechaExpiracion':pagare.fechaExpiracion,
        'lugarCumplimiento':pagare.lugarCumplimiento,
        'firma':pagare.firma,
        'ultimoEndoso':pagare.ultimoEndoso,
        'pendiente':pagare.pendiente,
        'etapa':pagare.etapa,
        'terminos':pagare.terminos,
        'codigoRetiro':pagare.codigoRetiro,
        'confirmacionRetiro':pagare.confirmacionRetiro,
        'hash_transaccion':pagare.hash_transaccion,
        'deudorAcepta':pagare.deudorAcepta,
        'acreedorAcepta':pagare.acreedorAcepta

    }
# --------Helper Methods------------


