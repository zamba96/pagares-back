from blockChainAccess import BlockChainAccess
from Pagare import Pagare
import time
import pandas as pd
import threading


def testPagare(i, nonce):
    pagare = Pagare()
    pagare.valor = i
    pagare._id = "{}:{}".format(nonce, i)
    pagare.nombreDeudor = "testDeudor"
    pagare.idDeudor = "100"
    pagare.nombreAcreedor = "testAcreedor"
    pagare.idAcreedor = "200"
    pagare.fechaCreacion = "10/10/2020"
    pagare.lugarCreacion = "Bogota"
    pagare.fechaVencimiento = "10/10/2021"
    pagare.fechaExpiracion = "10/10/2025"
    pagare.lugarCumplimiento = "Bogota"
    pagare.firma = "HEXXXXXX"
    pagare.ultimoEndoso = "null"
    pagare.pendiente = False
    pagare.etapa = 4
    pagare.terminos = "Test Terminos"
    pagare.codigoRetiro = "001"
    pagare.confirmacionRetiro = "null"
    pagare.hash_transaccion = "hash"
    pagare.deudorAcepta = True
    pagare.acreedorAcepta = True
    return pagare


bca = BlockChainAccess()


i = 0
total = 1000
testNum = []
timeList = []
while i < total:
    i = i + 1
    nonce = bca.getNonce()
    pagare = testPagare(i, nonce)
    start = time.time()
    print("Enviando transaccion {}/{}".format(i,total))
    stringHash, hexHash = bca.crear_pagare(pagare=pagare)
    print("Esperando transaccion {}/{}".format(i,total))
    bca.awaitTransaction(hexHash)
    end = time.time()
    dif_seconds = end - start
    print("Transaccion {}/{} termina en {} segundos".format(i, total, dif_seconds))
    testNum.append(i)
    timeList.append(dif_seconds)

d = {'test':testNum, 'time': timeList}
df = pd.DataFrame(data=d)
print(df)
df.to_csv('testTimes.csv')

