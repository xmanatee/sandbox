pragma solidity ^0.4.18;

contract Izum {

    mapping (address => bool) owners;

    mapping (address => string[]) certificates;

    function Izum() public {
        owners[msg.sender] = true;
    }

    modifier onlyOwners() {
    	require(owners[msg.sender]);
    	_;
    }

    // Modifiers
    function addOwner(address new_owner) onlyOwners() public {
        owners[new_owner] = true;
    }

    function addCertificate (address client, string cert) onlyOwners() public {
        certificates[client].push(cert);
    }

    // Getters
    function getCertificates (address client, uint8 i) constant public returns (string) {
        return certificates[client][i];
    }

    function getCertificatesNumber(address client) constant public returns (uint) {
        return certificates[client].length;
    }

}