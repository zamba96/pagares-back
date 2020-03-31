var pagareTracker = artifacts.require ("./pagareTracker.sol");

module.exports = function(deployer) {      
    deployer.deploy(pagareTracker);
}