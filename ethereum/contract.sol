pragma solidity ^0.4.18;

contract Order {
    enum PARTY_TYPE {STORE, STORAGE, DELIVERY}

    mapping (bytes32 => mapping (address => bool)) clients;

    modifier requireParty(bytes32 party) {
    	require(clients[party][msg.sender]);
    	_;
    }

    function addOwner(address new_owner) onlyOwners() public {
        owners[new_owner] = true;
    }

    function authorize(address new_owner) onlyOwners() public {
        clients[new_owner] = true;
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