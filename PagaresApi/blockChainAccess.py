from web3 import Web3
import json
from Pagare import Pagare
import binascii
from Endoso import Endoso
import requests
from ens import ENS
from pprint import pprint
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_account import Account


class BlockChainAccess:
    infura_url = 'https://ropsten.infura.io/v3/eb2fd22ee53744e7aa5c7f43b00536ba'
    ganache_url = "http://127.0.0.1:7545"
    account_1 = '0xCE7f6e712F227bAc123fD5939047Db2963E10d7F'  # Ropsten
    infura_wss = 'wss://ropsten.infura.io/ws/v3/eb2fd22ee53744e7aa5c7f43b00536ba'
    # account_1 = '0xE5cfc1B30018147c83E599d5D6Aa79b9fc26CF4a'  # Ganache

    pk = '37196d25e9c8ce0ab7e3ebfed765aa58cf5ff77f3499e790b60f342dcd0212ab'  # Ropsten
    # pk = '96f6e38c9334fab49ce3a08b8b2f74feb83259bbdd70c294698b104d516414ef'  # Ganache
    # account_2 = '0xdfeBbE784E15999C807e00125d7f10dc96A4Bc0b' # Fill me in
    # pk_1 = '3c554492f98ca1c8974a4f74db7fc78bae58ad8588a45cab3d330ed2aa7ea25c' # PK 1

    # web3 = Web3(Web3.HTTPProvider(infura_url))

    # Contract Address

    web3 = None
    contract = None
    ns = None

    def __init__(self):
        # self.web3 = Web3(Web3.HTTPProvider(self.ganache_url))

        self.web3 = Web3(Web3.HTTPProvider(self.infura_url))
        self.ns = ENS.fromWeb3(self.web3)
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
            with open('../truffle stuff/build/contracts/PagareTracker.json') as json_file:
                abi = json.load(json_file)['abi']

        self.contractAddress = self.web3.toChecksumAddress(
            '0x9D7F19128E83DcBa77271FEE9d72BD70C9fa2048')

        self.contract = self.web3.eth.contract(
            address=self.contractAddress, abi=abi)

        with open('resolver.json') as json_file:
            abi_resolver = json.load(json_file)

        with open('registry.json') as json_file:
            abi_registry = json.load(json_file)

        self.resolverAddress = self.web3.toChecksumAddress(
            '0x42D63ae25990889E35F215bC95884039Ba354115')
        self.resolverContract = self.web3.eth.contract(
            address=self.resolverAddress, abi=abi_resolver)

        self.registerAddress = self.web3.toChecksumAddress(
            '0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e')
        self.registryContract = self.web3.eth.contract(
            address=self.registerAddress, abi=abi_registry)

    # Methods
    # Info tiene las variables: fecha_creacion,fecha_vencimiento,fecha_expiracion,lugar_creacion,lugar_cumplimiento,firma

    def get_pagare_id(self, id_pagare):
        response = self.contract.functions.getPagareById(id_pagare).call()
        print(response)
        if(response[0] == ''):
            return None
        info_list = response[4].split(',')
        return_dict = {
            '_id': response[0],
            'valor': response[1],
            'idDeudor': response[2].split(',')[0],
            'nombreDeudor': response[2].split(',')[1],
            'idAcreedor': response[3].split(',')[0],
            'nombreAcreddor': response[3].split(',')[1],
            'fechaCreacion': info_list[0],
            'fechaVencimiento': info_list[1],
            'fechaExpiracion': info_list[2],
            'lugarCreacion': info_list[3],
            'lugarCumplimiento': info_list[4],
            'firma': info_list[5],
            'ultimoEndoso': response[5],
            'pendiente': response[6]
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
            'nonce': nonce,
        })
        signed_tx = self.web3.eth.account.sign_transaction(
            tx, private_key=self.pk)
        # print(signed_tx.hash)
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        # tx_hash = self.contract.functions.createPagare(pagare._id, str(pagare.valor), info_deudor, info_acreedor, info).transact({'from': self.account_1})
        tx_hash_string = "0x" + str(binascii.hexlify(tx_hash)).split("'")[1]
        return tx_hash_string
        # return "nope"

    def get_pure_pagare(self, id_pagare):
        response = self.contract.functions.getPagareById(id_pagare).call()
        return_dict = {
            '_id': response[0],
            'valor': response[1],
            'info_deudor': response[2],
            'info_acreedor': response[3],
            'info_extra': response[4],
            'ultimo_endoso': response[5],
            'pendiente': response[6]
        }
        return return_dict

    def endosar_pagare(self, endoso: Endoso):
        nonce = self.web3.eth.getTransactionCount(self.account_1)
        tx = self.contract.functions.endosarPagare(
            str(endoso.id_endosante) + ',' + endoso.nombre_endosante,
            str(endoso.id_endosatario) + ',' + endoso.nombre_endosatario,
            endoso.id_pagare,
            str(endoso.fecha),
            endoso.firma,
            endoso._id).buildTransaction({
                'nonce': nonce
            })
        signed_tx = self.web3.eth.account.sign_transaction(
            tx, private_key=self.pk)
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tx_hash_string = "0x" + str(binascii.hexlify(tx_hash)).split("'")[1]
        return tx_hash_string

    def get_endoso_id_blockchain(self, id_endoso):
        response = self.contract.functions.getEndosoById(id_endoso).call()
        print(response)
        if(response[0] == ''):
            return None
        endoso = Endoso()
        returnDict = endoso.from_blockchain(response)
        return returnDict

    def get_all_transaction_hashes(self):
        url = 'http://api-ropsten.etherscan.io/api?module=account&action=txlist&address=0x9D7F19128E83DcBa77271FEE9d72BD70C9fa2048&startblock=0&endblock=99999999&sort=asc&apikey=B8S6I3JS3FHX7Y6EQN3JDD2KI4THD6P495'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'}
        req = requests.get(url=url, headers=headers)

        data = req.json()['result']
        hashes = []
        del data[0]
        for a in data:
            hashes.append(a['hash'])
        return hashes

    def get_transaction_details(self, hash):
        transaction = self.web3.eth.getTransaction(hash)
        return transaction

    def get_all_transactions(self):
        hashes = self.get_all_transaction_hashes()
        returnList = []
        for hash in hashes:
            hexInput = self.get_transaction_details(hash)['input']
            f, decoded = self.contract.decode_function_input(hexInput)
            returnList.append({hash: decoded})
        # print(returnList)
        return returnList

    def create_subbomain(self, subdomain, owner):

        ns = self.ns
        eth_address = ns.address('pagaresvirtuales.test')
        # print(eth_address)
        name = '{}.pagaresvirtuales.test'.format(subdomain)
        # print("setup address")
        # print(self.web3.eth.accounts)
        acc = Account.from_key("0x" + self.pk)
        # print(acc.key)
        print(ns.owner('pagaresvirtuales.test'))
        # print(self.account_1)
        
        normalizedName = ns.nameprep(name)
        normalizedNode = ns.nameprep('pagaresvirtuales.test')
        normalizedLabel = ns.nameprep(subdomain)
        node = ns.namehash('pagaresvirtuales.test')
        wholeNameHash = ns.namehash(name)
        label = ns.namehash(normalizedLabel)
        label = self.web3.keccak(text=normalizedLabel)
        bytes_owner = self.registryContract.functions.owner(node).call()
        nonce = self.web3.eth.getTransactionCount(self.account_1)
        tx = self.registryContract.functions.setSubnodeOwner(node, label, owner).buildTransaction({
            'nonce': nonce,
            'from': self.account_1,
            'gas': 100000,
        })
        signed_tx = self.web3.eth.account.sign_transaction(
            tx, private_key=self.pk)
        # self.web3.middleware_onion.add(
        #     construct_sign_and_send_raw_middleware(acc))

        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tx_hash_string = "0x" + str(binascii.hexlify(tx_hash)).split("'")[1]

        print("Subnode created: {}, waiting for confirmation...".format(tx_hash_string))
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash, timeout=300)
        print("Subnode creation confirmed")
        return "OK"

        # SetAdr
        # nonce = self.web3.eth.getTransactionCount(self.account_1)
        # tx = self.resolverContract.functions.setAddr(wholeNameHash, owner).buildTransaction({
        #     'nonce': nonce,
        #     'from': self.account_1,
        #     'gas': 100000,
        # })
        # signed_tx = self.web3.eth.account.sign_transaction(
        #     tx, private_key=self.pk)
        # # self.web3.middleware_onion.add(
        # #     construct_sign_and_send_raw_middleware(acc))

        # tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        # tx_hash_string = "0x" + str(binascii.hexlify(tx_hash)).split("'")[1]

        # print("Address Set: {}, waiting for confirmation...".format(tx_hash_string))
        # tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash, timeout=300)
        # print("Address set confirmed")

    def get_owner_domain(self, domain):
        ns = self.ns
        return ns.owner(domain)

    def get_address_from_name(self, domain):
        ns = self.ns
        return ns.address(domain)
if __name__ == '__main__':
    bca = BlockChainAccess()
    # pprint(bca.get_all_transactions())
    newOwner = '0xfabc9d025e7B0F7720300c1F99a57fd6e4413934'  # testaccount 3
    # bca.create_subbomain('prueba4', bca.account_1)
    print(bca.get_owner_domain('prueba4.pagaresvirtuales.test'))
    print(bca.get_address_from_name('prueba4.pagaresvirtuales.test'))
