var ENS = require('ethereum-ens');
var web3 = require('web3');
var Accounts = require('web3-eth-accounts');

privateKey = '37196d25e9c8ce0ab7e3ebfed765aa58cf5ff77f3499e790b60f342dcd0212ab'
account_1 = '0xCE7f6e712F227bAc123fD5939047Db2963E10d7F'
account = web3.eth.accounts.privateKeyToAccount(privateKey);
web3.eth.accounts.wallet.add(account);
console.log(web3.eth.accounts)