from web3 import Web3
import json
import binascii
import requests
from ens import ENS
from pprint import pprint
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_account import Account
from time import sleep
import time
import datetime


class BlockChainAccess:
    infura_url = 'https://ropsten.infura.io/v3/eb2fd22ee53744e7aa5c7f43b00536ba'
    ganache_url = "http://127.0.0.1:7545"
    # account_1 = '0xCE7f6e712F227bAc123fD5939047Db2963E10d7F'  # Ropsten
    # infura_wss = 'wss://ropsten.infura.io/ws/v3/eb2fd22ee53744e7aa5c7f43b00536ba'
    account_1 = '0xF9b3Ffc373BD0990FC2276F23aa176Be1B0ab3b0'  # Ganache
    account_2 = '0xe6B5b0F337fe6991cffAc4B8845f27dBa242A62b' # Ganache
    account_3 = '0xc2899aDdB87c7b85602Df08ebCAB3A5489336F88' # Ganache


    # pk = '37196d25e9c8ce0ab7e3ebfed765aa58cf5ff77f3499e790b60f342dcd0212ab'  # Ropsten
    pk = 'fc9b343d17e960c4f3c834d234c47039b5b968d58d7c90c04eb61aef8a70603b'  # Ganache
    pk2 = '68c607ca096d0f5128af14558984c05eeefab34c72f549e35c477651a3381428' # Ganache
    # account_2 = '0xdfeBbE784E15999C807e00125d7f10dc96A4Bc0b' # Fill me in
    # pk_1 = '3c554492f98ca1c8974a4f74db7fc78bae58ad8588a45cab3d330ed2aa7ea25c' # PK 1

    # web3 = Web3(Web3.HTTPProvider(infura_url))

    # Contract Address

    web3 = None
    contract = None
    ns = None

    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(self.ganache_url))

        # self.web3 = Web3(Web3.HTTPProvider(self.infura_url))
        # self.ns = ENS.fromWeb3(self.web3)
        # self.web3 = Web3(Web3.WebsocketProvider(self.infura_wss))
        if(not self.web3.isConnected()):
            print("-------------------Blockchain Access--------------------------")
            print('Connection to {}: Failed\nExiting...'.format(self.web3.provider))
            print("--------------------------------------------------------------")
            exit()
        else:
            print("-------------------Blockchain Access--------------------------")
            print('Connection to {}: established'.format(self.web3.provider))
            print("--------------------------------------------------------------")
            with open('../truffle stuff/build/contracts/PagareVirtual.json') as json_file:
                abi = json.load(json_file)['abi']

        self.contractAddress = self.web3.toChecksumAddress(
            '0xBaED9A8044Cc53580D800058B5AEb729aBE99698')

        self.contract = self.web3.eth.contract(
            address=self.contractAddress, abi=abi)

    def createPagare(self, acc_from, acc_to, fecha_cre, fecha_venc,info, pk):
        bca = self
        nonce = bca.web3.eth.getTransactionCount(bca.account_1)
        
        # Crear pagare
        tx = bca.contract.functions.createPagare(acc_to, info, fecha_cre, fecha_venc).buildTransaction({
            'nonce': nonce,
            'value': 1000000000000000000,
            'from' : acc_from
        })
        signed_tx = bca.web3.eth.account.sign_transaction(
            tx, private_key=pk)
        tx_hash = bca.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tx_hash_string = "0x" + str(binascii.hexlify(tx_hash)).split("'")[1]
        print(tx_hash_string)
        sleep(2)

    # Methods

info = 'Pagare Prueba 1'
timestamp_hoy = int(time.time())
datetime_one_year = datetime.date(2021,5,12)
timestamp_one_year = int(time.mktime(datetime_one_year.timetuple()))
datetime_2daysago = datetime.date(2020,5,9)
timestamp_2daysago = int(time.mktime(datetime_2daysago.timetuple()))
bca = BlockChainAccess()
# Crear pagare
bca.createPagare(bca.account_1, bca.account_2, timestamp_2daysago, timestamp_one_year, info, bca.pk)
pagares = bca.contract.functions.getIdPagaresDeudor(bca.account_2).call()
print("Pagares deudor account 2: \n{}".format(pagares))

# Firmar con account 2
nonce = bca.web3.eth.getTransactionCount(bca.account_2)
# tx = bca.contract.functions.firmarPagare(id_fimrar).buildTransaction({
#     'nonce': nonce,
#     'from' : bca.account_2
# })
# signed_tx = bca.web3.eth.account.sign_transaction(
#     tx, private_key=bca.pk2)
# tx_hash = bca.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
# tx_hash_string = "0x" + str(binascii.hexlify(tx_hash)).split("'")[1]
# print(tx_hash_string)
sleep(2)
pagares = bca.contract.functions.getIdPagaresAcreedor(bca.account_1).call()
print("Pagares acreedor account 1: \n{}".format(pagares))
pagare = bca.contract.functions.getPagareById(1).call()
print("Pagare 0\n{}".format(pagare))

# Endoso 1 de acount 1 a account 3
nonce = bca.web3.eth.getTransactionCount(bca.account_1)
# tx = bca.contract.functions.endosarPagare(bca.account_3, 0, timestamp_hoy,).buildTransaction({
#     'nonce': nonce,
#     'from' : bca.account_1
# })
# signed_tx = bca.web3.eth.account.sign_transaction(
#     tx, private_key=bca.pk)
# tx_hash = bca.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
# tx_hash_string = "0x" + str(binascii.hexlify(tx_hash)).split("'")[1]
# print(tx_hash_string)
sleep(2)
pagares = bca.contract.functions.getEndososPagare(0).call()
# print("endosos pagare 0:\n{}".format(pagares))
endoso = bca.contract.functions.getEndosoById(1).call()
# print("Endoso 1: \n{}".format(endoso))

# Devolver dinero pagare 0
# tx = bca.contract.functions.devolverDinero(1).buildTransaction({
#     'nonce': nonce,
#     'from' : bca.account_1
# })
# signed_tx = bca.web3.eth.account.sign_transaction(
#     tx, private_key=bca.pk)
# tx_hash = bca.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
# tx_hash_string = "0x" + str(binascii.hexlify(tx_hash)).split("'")[1]
# print(tx_hash_string)
sleep(2)

pagare = bca.contract.functions.getPagareById(1).call()
print("Pagare 0 after dev\n{}".format(pagare))
print(bca.contract.functions.esDeudorDe(bca.account_2, 1).call())