from web3 import Web3
import json
from Pagare import Pagare


class BlockChainAccess:
    infura_url = 'https://ropsten.infura.io/v3/eb2fd22ee53744e7aa5c7f43b00536ba'
    ganache_url = "http://127.0.0.1:7545"
    account_1 = '0x0Faa4E21C6E331a1c81f6c531a6DcaBD187642a1'  # Fill me in
    # account_2 = '0xdfeBbE784E15999C807e00125d7f10dc96A4Bc0b' # Fill me in
    # pk_1 = '3c554492f98ca1c8974a4f74db7fc78bae58ad8588a45cab3d330ed2aa7ea25c' # PK 1

    # web3 = Web3(Web3.HTTPProvider(infura_url))
    web3 = None
    contract = None
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(self.ganache_url))
        # global web3 = Web3(Web3.HTTPProvider(infura_url))
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
        '0x25871EE82144843454707FC9A2f5335c1b5E239a')

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
        info = pagare
        



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