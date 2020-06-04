var pagareTracker = artifacts.require ("./pagareTracker.sol");
var pagareVirtual = artifacts.require("./pagareVirtual.sol")

module.exports = function(deployer) {      
    deployer.deploy(pagareTracker);
    deployer.deploy(pagareVirtual)
}