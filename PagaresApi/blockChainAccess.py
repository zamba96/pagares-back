from web3 import Web3
import json
from Pagare import Pagare
import binascii

class BlockChainAccess:
    infura_url = 'https://ropsten.infura.io/v3/eb2fd22ee53744e7aa5c7f43b00536ba'
    ganache_url = "http://127.0.0.1:7545"
    account_1 = '0xCE7f6e712F227bAc123fD5939047Db2963E10d7F'  # Fill me in

    pk = '37196d25e9c8ce0ab7e3ebfed765aa58cf5ff77f3499e790b60f342dcd0212ab'
    # account_2 = '0xdfeBbE784E15999C807e00125d7f10dc96A4Bc0b' # Fill me in
    # pk_1 = '3c554492f98ca1c8974a4f74db7fc78bae58ad8588a45cab3d330ed2aa7ea25c' # PK 1

    # web3 = Web3(Web3.HTTPProvider(infura_url))
    web3 = None
    contract = None
    def __init__(self):
        # self.web3 = Web3(Web3.HTTPProvider(self.ganache_url))
        self.web3 = Web3(Web3.HTTPProvider(self.infura_url))
        if(not self.web3.isConnected()):
            print("-------------------Blockchain Access--------------------------")
            print('Connection to {}: Failed\nExiting...'.format(self.web3.provider))
            print("--------------------------------------------------------------")
        else:
            print("-------------------Blockchain Access--------------------------")
            print('Connection to {}: established'.format(self.web3.provider))
            print("--------------------------------------------------------------")
            with open('../truffle stuff/build/contracts/PagareTracker.json') as json_file:
                abi = json.load(json_file)['abi']

        contractAddress = self.web3.toChecksumAddress(
        '0x68a9e87DDccB21B7222051c89B96ad4770eA6644')

        self.contract = self.web3.eth.contract(address=contractAddress, abi=abi)





    # Methods
    # Info tiene las variables: fecha_creacion,fecha_vencimiento,fecha_expiracion,lugar_creacion,lugar_cumplimiento,firma
    def get_pagare_id(self, id_pagare):
        response = self.contract.functions.getPagareById(id_pagare).call()
        print(response)
        if(response[0] == ''):
            return None
        info_list = response[4].split(',')
        return_dict = {
            '_id':response[0],
            'valor':response[1],
            'idDeudor':response[2].split(',')[0],
            'nombreDeudor':response[2].split(',')[1],
            'idAcreedor':response[3].split(',')[0],
            'nombreAcreddor':response[3].split(',')[1],
            'fechaCreacion':info_list[0],
            'fechaVencimiento':info_list[1],
            'fechaExpiracion':info_list[2],
            'lugarCreacion':info_list[3],
            'lugarCumplimiento':info_list[4],
            'firma':info_list[5],
            'ultimoEndoso':response[5],
            'pendiente':response[6]
        }
        return return_dict
    
    def crear_pagare(self, pagare: Pagare):
        info = str(pagare.fechaCreacion) + ','
        info = info + str(pagare.fechaVencimiento) + ',' 
        info = info + str(pagare.fechaExpiracion) + ',' 
        info = info + pagare.lugarCreacion + ',' 
        info = info + pagare.lugarCumplimiento + ',' 
        info = info + pagare.firma
        info_acreedor = str(pagare.idAcreedor) + ',' + pagare.nombreAcreedor
        info_deudor = str(pagare.idDeudor) + ',' + pagare.nombreDeudor 
        nonce = self.web3.eth.getTransactionCount(self.account_1) 
        tx = self.contract.functions.createPagare(pagare._id, str(pagare.valor), info_deudor, info_acreedor, info).buildTransaction({
            'nonce':nonce
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.pk)
        # print(signed_tx.hash)
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        # tx_hash = self.contract.functions.createPagare(pagare._id, str(pagare.valor), info_deudor, info_acreedor, info).transact({'from': self.account_1})
        tx_hash_string = "0x" + str(binascii.hexlify(tx_hash)).split("'")[1]
        return tx_hash_string
        # return "nope"


    def get_pure_pagare(self, id_pagare):
        response = self.contract.functions.getPagareById(id_pagare).call()
        return_dict = {
            '_id':response[0],
            'valor':response[1],
            'info_deudor':response[2],
            'info_acreedor':response[3],
            'info_extra':response[4],
            'ultimo_endoso':response[5],
            'pendiente':response[6]
        }
        return return_dict


    # tx_hash = contract.functions.createPagare(
    #     '002', '10', '1010,Juan', '1020,Ernesto', '10-10-10,10-02-11,10-10-15,Bogota,Bogota,FIRMA_OR_WHATEVER').transact({'from': account_1})
    # tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    # tx_hash = contract.functions.transferPagare(
    #     '1020', '1030', '001', '10-10-10', 'firma endoso', '101').transact({'from': account_1})
    # tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    # tx_hash = contract.functions.transferPagare(
    #     '1030', '1020', '001', '10-10-10', 'firma endoso', '102').transact({'from': account_1})
    # tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    # print(get_pagare_id('002'))