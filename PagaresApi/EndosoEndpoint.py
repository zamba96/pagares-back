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
from Endoso import Endoso

dateFormatStr = '%d-%m-%Y'


def get_endoso_id_blockchain(bca: BlockChainAccess, id_endoso):
    endoso = bca.get_endoso_id_blockchain(id_endoso)
    return endoso