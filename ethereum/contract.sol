pragma solidity ^0.4.13;

contract OrderNegotiator {

    enum PARTY_TYPE {STORE, STORAGE, DELIVERY, ADMIN}
    mapping (bytes32 => mapping (address => bool)) clients;

    enum ORDER_STATUS {
        DEFAULT,
        PLACED,
        STORAGE_RECEIVED,
        STORAGE_RELEASED,
        DELIVERY_RECEIVED,
        DELIVERY_RELEASED,
        CLIENT_RECEIVED
    }

    struct Order {
        ORDER_STATUS status;
        uint value;
        address store_addr;
        address storage_addr;
        address delivery_addr;
        address client_addr;
    }
    mapping (bytes32 => Order) orders;

    uint constant STORAGE_FEE = 1000;
    uint constant DELIVERY_FEE = 1000;

    modifier requireParty(PARTY_TYPE party) {
        require(clients[sha3(party)][msg.sender]);
        _;
    }

    modifier requireOrderStatus(bytes32 order_id, ORDER_STATUS status) {
        require(orders[order_id].status == status);
        _;
    }

    function add_authority(bytes32 party, address addr) requireParty(PARTY_TYPE.ADMIN) public {
        clients[party][addr] = true;
    }

    // Transition functions for order status

    function store_place_order(bytes32 order_id, address client_addr) requireParty(PARTY_TYPE.STORE) requireOrderStatus(order_id, ORDER_STATUS.DEFAULT) public payable {
        require(msg.value >= STORAGE_FEE + DELIVERY_FEE);
        orders[order_id] = Order(ORDER_STATUS.PLACED, msg.value, msg.sender, 0, 0, client_addr);
    }

    function storage_receive(bytes32 order_id) requireParty(PARTY_TYPE.STORAGE) requireOrderStatus(order_id, ORDER_STATUS.PLACED) public {
        orders[order_id].status = ORDER_STATUS.STORAGE_RECEIVED;
        orders[order_id].storage_addr = msg.sender;
    }

    function storage_release(bytes32 order_id) requireParty(PARTY_TYPE.STORAGE) requireOrderStatus(order_id, ORDER_STATUS.STORAGE_RECEIVED) public {
        orders[order_id].status = ORDER_STATUS.STORAGE_RELEASED;
    }

    function delivery_receive(bytes32 order_id) requireParty(PARTY_TYPE.DELIVERY) requireOrderStatus(order_id, ORDER_STATUS.STORAGE_RELEASED) public {
        orders[order_id].status = ORDER_STATUS.DELIVERY_RECEIVED;
        orders[order_id].delivery_addr = msg.sender;
    }

    function delivery_release(bytes32 order_id) requireParty(PARTY_TYPE.DELIVERY) requireOrderStatus(order_id, ORDER_STATUS.DELIVERY_RECEIVED) public {
        orders[order_id].status = ORDER_STATUS.DELIVERY_RELEASED;
    }

    function client_receive(bytes32 order_id) requireOrderStatus(order_id, ORDER_STATUS.DELIVERY_RELEASED) public {
        require(msg.sender == orders[order_id].client_addr);
        orders[order_id].status = ORDER_STATUS.CLIENT_RECEIVED;
    }


    // All the parties get payed
    function storage_withdraw_fee(bytes32 order_id) requireOrderStatus(order_id, ORDER_STATUS.CLIENT_RECEIVED) public {
        require(msg.sender == orders[order_id].storage_addr);
        msg.sender.transfer(STORAGE_FEE);
        orders[order_id].storage_addr = 0;
    }

    function delivery_withdraw_fee(bytes32 order_id) requireOrderStatus(order_id, ORDER_STATUS.CLIENT_RECEIVED) public {
        require(msg.sender == orders[order_id].delivery_addr);
        msg.sender.transfer(DELIVERY_FEE);
        orders[order_id].delivery_addr = 0;
    }

    function store_close_order(bytes32 order_id) requireOrderStatus(order_id, ORDER_STATUS.CLIENT_RECEIVED) public {
        require(msg.sender == orders[order_id].store_addr);
        require(orders[order_id].storage_addr == 0);
        require(orders[order_id].delivery_addr == 0);

        msg.sender.transfer(orders[order_id].value - STORAGE_FEE - DELIVERY_FEE);

        delete orders[order_id];
    }

    function get_order_status(bytes32 order_id) constant public returns (ORDER_STATUS) {
        return orders[order_id].status;
    }

}