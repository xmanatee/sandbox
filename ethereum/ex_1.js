const public_keys = [
    "0x5b77c2a2079173576116d0d85169334e4f129e4a",
    "0x68ee7c90f5316672cd7ea2922cdbed1637a5d31b",
    "0xc1bc58d47caf6a5cc7aaa259fb9e5917abda1c1c",

    "0x16086437cec89335c945045235881da4da816f57",
    "0x1b2f032d80ae86bfe049c16717c56ecc7539546a",
    "0xebb6f9e92244cfbb628c747b0222e4560ab3dd6c",
    "0xdf50396992f741829c76749449dc0905b142d913",
    "0x9c482306723e89d1c67a29f32a6e84292b5b4d16",
    "0x81860d567da6fc12a27319d8c470fb9e643aec46",
    "0xd1bfba28fb74cc2f01283e854dfd2d6024a5bbba",
];

const private_keys = [
    "07cee9c04ab35664e38d55277b2bcb723b94e59392f58018b77945fcc36e572d",
    "70bcd6987e6cac167ec2e6b1785228771d1df03973149e1cdfdb63134d5f6594",
    "0603e6fceb167b3fea86a014316f60f4178937f5eb390f39d03f0281360e80cd",
    "3f2fc33bdc68d36ac7154749b487cc85f7ff778dce8ee0bdce90745b3353acb7",
    "77ff27f2ebd3a2364a2b4c31f37626a289dba5863cf280aecf0b1d206b78930a",
    "c45836ef02df634fcc2350a5394e8165518b99f9b653e7a9de7f0379470f3f80",
    "77140c6f2483f5d57ee3cdc383286bb02963178c67036b6fe74b59b54babc3fd",
    "1dc2b491be34cffaac71ea72dd5091b0914a551b781e67592b87b1fe6bb60b31",
    "c5654bab98957b6fd3216ed67105800ce9bf82dc08bcb58345ddec12fef3c3f8",
    "f481cb4af396e80a0e261461a7ede45656cddbcba761c51c36af9b14b4280705",
];

const fs = require('fs');
const solc = require('solc');
const Web3 = require('web3');

// Connect to local Ethereum node
const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));

// Compile the source code
const input = fs.readFileSync('contracts/izum.sol');
const output = solc.compile(input.toString(), 1);
const bytecode = output.contracts['Token'].bytecode;
const abi = JSON.parse(output.contracts['Token'].interface);

// Contract object
const contract = web3.eth.contract(abi);

// Deploy contract instance
const contractInstance = contract.new({
    data: '0x' + bytecode,
    from: public_keys[0],
    gas: 90000*2
}, (err, res) => {
    if (err) {
        console.log(err);
        return;
    }

    // Log the tx, you can explore status with eth.getTransaction()
    console.log(res.transactionHash);

    // If we have an address property, the contract was deployed
    if (res.address) {
        console.log('Contract address: ' + res.address);
        // Let's test the deployed contract
        testContract(res.address);
    }
});

// Quick test the contract

function testContract(address) {
    // Reference to the deployed contract
    const token = contract.at(address);
    // Destination account for test
    const dest_account = '0x002D61B362ead60A632c0e6B43fCff4A7a259285';

    // Assert initial account balance, should be 100000
    const balance1 = token.balances.call(web3.eth.coinbase);
    console.log(balance1 == 1000000);

    // Call the transfer function
    token.transfer(dest_account, 100, {from: web3.eth.coinbase}, (err, res) => {
        // Log transaction, in case you want to explore
        console.log('tx: ' + res);
        // Assert destination account balance, should be 100
        const balance2 = token.balances.call(dest_account);
        console.log(balance2 == 100);
    });
}