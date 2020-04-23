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
import EndosoEndpoint
from Endoso import Endoso

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
    pagare.etapa = request.json['etapa']

    updates = getUpdateStatement(pagare)

    db.pagares.update_one({'_id':ObjectId(id_pagare)}, {'$set': updates})
    doc = db.pagares.find_one({'_id':ObjectId(id_pagare)})
    pagare.pagareFromDoc(doc)
    return vars(pagare)


# Route /pagares/<id_pagare>/etapa2/aceptar
# PUT
# Acepta el pagare
@app.route('/pagares/<id_pagare>/etapa2/aceptar', methods=['PUT'])
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
        if pagare.ultimoEndoso == "null":
            returnList.append(vars(pagare))
    
    endosos = db.endosos.find({"id_endosatario": int(id_acreedor), "es_ultimo_endoso": True})
    # print(list(endosos))
    for e in list(endosos):
        pagare = Pagare()
        doc = db.pagares.find_one({"_id": ObjectId(e['id_pagare'])})
        pagare.pagareFromDoc(doc)
        returnList.append(vars(pagare))
    return jsonify(returnList)


# Route /endosos/<id_endoso>/blockchain
# GET
# Trae el endoso con id dado del blockchain
@app.route('/endosos/<id_endoso>/blockchain', methods=['GET'])
def get_endoso_id_blockchain(id_endoso):
    endoso = EndosoEndpoint.get_endoso_id_blockchain(bca, id_endoso)
    if endoso == None:
        return "No existe el endoso en el blockchain :(", 404
    return endoso

# Route /endosos/endosante/<id_endosante>
# GET
# Trae endosos realizados por el endosante con el id dado
@app.route('/endosos/endosante/<id_endosante>', methods=['GET'])
def get_endoso_endosante(id_endosante):
    endosos = db.endosos.find({"id_endosante" : int(id_endosante)})
    pagaresList = list(endosos)
    returnList = []
    for e in pagaresList:
        endoso = Endoso()
        endoso.endosoFromDoc(e)
        returnList.append(vars(endoso))
    return jsonify(returnList)

# Route /endosos/endosatario/<id_endosatario>
# GET
# Trae endosos realizados por el endosatario con el id dado
@app.route('/endosos/endosatario/<id_endosatario>', methods=['GET'])
def get_endoso_endosatario(id_endosatario):
    endosos = db.endosos.find({"id_endosatario" : int(id_endosatario)})
    pagaresList = list(endosos)
    returnList = []
    for e in pagaresList:
        endoso = Endoso()
        endoso.endosoFromDoc(e)
        returnList.append(vars(endoso))
    return jsonify(returnList)

# Route /endosos/<id_endoso>
# GET
# Trae el endoso con id dado 
@app.route('/endosos/<id_endoso>', methods=['GET'])
def get_endoso_id(id_endoso):
    try:
        doc = db.endosos.find_one({"_id": ObjectId(id_endoso)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Endoso no encontrado", 404
    endoso = Endoso()
    endoso.endosoFromDoc(doc)
    return vars(endoso)



# Route /pagares/<id_pagare>/endosos
# POST
# Crea un endoso para el pagare con id dado
@app.route('/pagares/<id_pagare>/endosos', methods=['POST'])
def crear_endoso(id_pagare):
    try:
        doc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Pagare no encontrado", 404
    
    pagare = Pagare()
    pagare.pagareFromDoc(doc)
    anterior_endoso = pagare.ultimoEndoso
    endoso = Endoso()
    endoso.endosoFromRequest(request, id_pagare, anterior_endoso)
    # Revisar que el endoso sea valido
    if not pagare.pendiente:
        return "Error: El pagare {} no está pendiente, puede ser que está vencido o algo".format(pagare._id)
    if pagare.ultimoEndoso == "null" and endoso.id_endosante != pagare.idAcreedor:
        return "Error: {} no es el acreedor actual del pagare {}".format(endoso.nombre_endosante, id_pagare), 401
    if pagare.ultimoEndoso != "null":
        ultimoEndoso = Endoso()
        ultimoEndoso.endosoFromDoc(db.endosos.find_one({"_id":ObjectId(pagare.ultimoEndoso)}))
        if ultimoEndoso.id_endosatario != endoso.id_endosante:
            return "Error: {} no es el acreedor actual del pagare {}".format(endoso.nombre_endosante, id_pagare), 401
    # Agregar endoso a db
    id_insertado = db.endosos.insert_one(vars(endoso)).inserted_id
    endoso._id = str(id_insertado)
    # Agregar Endoso a BC
    tx_hash = bca.endosar_pagare(endoso)
    endoso.hash_transaccion = tx_hash
    #Actualizar Pagare
    pagare.ultimoEndoso = endoso._id
    pagareUpdates = getUpdateStatement(pagare)
    db.pagares.update_one({'_id':ObjectId(id_pagare)}, {'$set': pagareUpdates})
    #actualizar endoso
    db.endosos.update_one({'_id':ObjectId(endoso._id)}, {'$set': {
        'hash_transaccion':tx_hash,
        }})
    doc = db.endosos.find_one({'_id':ObjectId(endoso._id)})
    endosoR = Endoso()
    endosoR.endosoFromDoc(doc)
    return vars(endosoR)

# GET
# Retorna todos los endosos actuales de la DB para el pagare dado
@app.route('/pagares/<id_pagare>/endosos', methods=['GET'])
def get_endosos_by_pagare(id_pagare):
    endosos = db.endosos.find({'id_pagare':id_pagare})
    pagaresList = list(endosos)
    returnList = []
    for e in pagaresList:
        endoso = Endoso()
        endoso.endosoFromDoc(e)
        returnList.append(vars(endoso))
    return jsonify(returnList)


# Route /pagares/<id_pagare>/ultimo_endoso
# Retorna el ultimo endoso del pagare con el ID
@app.route('/pagares/<id_pagare>/ultimo_endoso')
def get_ultimo_endoso(id_pagare):
    try:
        doc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Pagare no encontrado", 404
    pagare = Pagare()
    pagare.pagareFromDoc(doc)
    if pagare.ultimoEndoso == "null":
        return "El pagare {} no tiene endosos".format(pagare._id), 404
    doc = db.endosos.find_one({"_id":ObjectId(pagare.ultimoEndoso)})
    endoso = Endoso()
    endoso.endosoFromDoc(doc)
    return vars(endoso)
    

# Route /endosos 
# GET
# Retorna todos los endosos actuales de la DB para el pagare dado
@app.route('/endosos', methods=['GET'])
def get_endosos():
    endosos = db.endosos.find()
    pagaresList = list(endosos)
    returnList = []
    for e in pagaresList:
        endoso = Endoso()
        endoso.endosoFromDoc(e)
        returnList.append(vars(endoso))
    return jsonify(returnList)


# Route /pagares/<id_pagares>/endosos/etapa1
# POST
# Crea un nuevo endoso en etapa 1
@app.route('/pagares/<id_pagare>/endosos/etapa1', methods=['POST'])
def endosar_etapa_1(id_pagare):
    try:
        doc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Pagare no encontrado", 404
    pagare = Pagare()
    pagare.pagareFromDoc(doc)
    # Revisar que no exista endoso pendiente
    doc = db.endosos.find_one({"id_pagare": id_pagare, "etapa":1})
    if doc != None:
        return "Ya existe un endoso con id {} en proceso para el pagare {}".format(doc["_id"], id_pagare), 401

    # Revisar legitimo tenedor
    if not pagare.pendiente:
        return "Error: El pagare {} no está pendiente, puede ser que está vencido o algo".format(pagare._id)
    if pagare.ultimoEndoso == "null" and request.json['id_endosante'] != pagare.idAcreedor:
        return "Error: {} no es el acreedor actual del pagare {}".format(request.json['nombre_endosante'], id_pagare), 401
    if pagare.ultimoEndoso != "null":
        ultimoEndoso = Endoso()
        ultimoEndoso.endosoFromDoc(db.endosos.find_one({"_id":ObjectId(pagare.ultimoEndoso)}))
        if ultimoEndoso.id_endosatario != request.json['id_endosante']:
            return "Error: {} no es el acreedor actual del pagare {}".format(request.json['nombre_endosante'], id_pagare), 401
    # Crear endoso
    endoso = Endoso()
    endoso.etapa = 1
    endoso.id_endosante = request.json['id_endosante']
    endoso.id_endosatario = request.json['id_endosatario']
    endoso.nombre_endosante = request.json['nombre_endosante']
    endoso.nombre_endosatario = request.json['nombre_endosatario']
    endoso.id_anterior_endoso = pagare.ultimoEndoso
    endoso.id_pagare = id_pagare
    
    # Send to DB
    inserted_id = db.endosos.insert_one(vars(endoso)).inserted_id

    # get the new endoso
    endoso._id = str(inserted_id)
    return vars(endoso)

# Route: /pagares/<id_pagare>/endosos/etapa2
# POST
# Crea un endoso en etapa2 
@app.route('/pagares/<id_pagare>/endosos/etapa2', methods=['POST'])
def crear_endoso_etapa_2(id_pagare):
    try:
        doc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Pagare no encontrado", 404
    
    pagare = Pagare()
    pagare.pagareFromDoc(doc)
    endoso = Endoso()
    docEndoso = db.endosos.find_one({"id_pagare":id_pagare, "etapa": 1})
    if docEndoso == None:
        return "No existe un endoso pendiente (en etapa 2) para el pagare designado", 401
    endoso.endosoFromDoc(docEndoso)
    # Revisar que el endoso sea valido
    if not pagare.pendiente:
        return "Error: El pagare {} no está pendiente, puede ser que está vencido o algo".format(pagare._id)
    if pagare.ultimoEndoso == "null" and endoso.id_endosante != pagare.idAcreedor:
        return "Error: {} no es el acreedor actual del pagare {}".format(endoso.nombre_endosante, id_pagare), 401
    if pagare.ultimoEndoso != "null":
        ultimoEndoso = Endoso()
        ultimoEndoso.endosoFromDoc(db.endosos.find_one({"_id":ObjectId(pagare.ultimoEndoso)}))
        if ultimoEndoso.id_endosatario != endoso.id_endosante:
            return "Error: {} no es el acreedor actual del pagare {}".format(endoso.nombre_endosante, id_pagare), 401
    # agregar codigo de retiro
    endoso.codigo_retiro = request.json['codigo_retiro']
    endoso.etapa = 2
    #actualizar endoso
    db.endosos.update_one({'_id':ObjectId(endoso._id)}, {'$set':{
        "codigo_retiro": endoso.codigo_retiro,
    }})
    return vars(endoso)

# Route: /pagares/<id_pagare>/endosos/etapa3
# POST
# Crea un endoso en etapa3 (final)
@app.route('/pagares/<id_pagare>/endosos/etapa3', methods=['POST'])
def crear_endoso_etapa_3(id_pagare):
    try:
        doc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Pagare no encontrado", 404
    
    pagare = Pagare()
    pagare.pagareFromDoc(doc)
    anterior_endoso = pagare.ultimoEndoso
    endoso = Endoso()
    docEndoso = db.endosos.find_one({"id_pagare":id_pagare, "etapa": 2})
    if docEndoso == None:
        return "No existe un endoso pendiente (en etapa 3) para el pagare designado", 401
    endoso.endosoFromDoc(docEndoso)
    # Revisar que el endoso sea valido
    if not pagare.pendiente:
        return "Error: El pagare {} no está pendiente, puede ser que está vencido o algo".format(pagare._id)
    if pagare.ultimoEndoso == "null" and endoso.id_endosante != pagare.idAcreedor:
        return "Error: {} no es el acreedor actual del pagare {}".format(endoso.nombre_endosante, id_pagare), 401
    if pagare.ultimoEndoso != "null":
        ultimoEndoso = Endoso()
        ultimoEndoso.endosoFromDoc(db.endosos.find_one({"_id":ObjectId(pagare.ultimoEndoso)}))
        if ultimoEndoso.id_endosatario != endoso.id_endosante:
            return "Error: {} no es el acreedor actual del pagare {}".format(endoso.nombre_endosante, id_pagare), 401
    # Termina de llenar el endoso
    endoso.es_ultimo_endoso = True
    endoso.etapa = 3
    endoso.firma = request.json['firma']
    endoso.fecha = datetime.today()
    # Agregar Endoso a BC
    tx_hash = bca.endosar_pagare(endoso)
    endoso.hash_transaccion = tx_hash
    #Actualizar Pagare
    pagare.ultimoEndoso = endoso._id
    pagareUpdates = getUpdateStatement(pagare)
    db.pagares.update_one({'_id':ObjectId(id_pagare)}, {'$set': pagareUpdates})
    #actualizar endoso
    db.endosos.update_one({'_id':ObjectId(endoso._id)}, {'$set':{
        "firma": endoso.firma,
        "fecha": endoso.fecha,
        "etapa": 3,
        "es_ultimo_endoso": True,
        "hash_transaccion": tx_hash

    }})
    # Actualizar anterior endoso
    if anterior_endoso != "null":
        db.endosos.update_one({"_id":ObjectId(anterior_endoso)}, {"$set": {"es_ultimo_endoso": False} })
    doc = db.endosos.find_one({'_id':ObjectId(endoso._id)})
    endosoR = Endoso()
    endosoR.endosoFromDoc(doc)
    return vars(endosoR)

# DELETE
# Borra el endoso en etapa 1 del pagaré con el id dado
@app.route('/pagares/<id_pagare>/endosos/etapa1', methods=['DELETE'])
def delete_pagare_1(id_pagare):
    try:
        doc = db.pagares.find_one({"_id": ObjectId(id_pagare)})
    except:
        return "El id es invalido", 400 
    if doc == None:
        return "Pagare no encontrado", 404
    if doc['ultimoEndoso'] == "null":
        return "No existe un endoso", 304
    doc2 = db.endosos.delete_one({"id_pagare": id_pagare, "etapa":1}).deleted_count
    print(doc2)
    return str(doc2)


@app.route('/transacciones', methods=['GET'])
def get_all_transactions():
    return jsonify(bca.get_all_transactions())


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


