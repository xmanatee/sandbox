pragma solidity ^0.4.13;

contract OrderNegotiator {

    enum PARTY_TYPE {NONE, STORAGE, DELIVERY, ADMIN}
    mapping (bytes32 => mapping (address => bool)) clients;

    enum ORDER_STATUS {
        DEFAULT,
        PLACED,
        DELIVERY_RECEIVED,
        DELIVERY_RELEASED,
        STORAGE_RECEIVED,
        STORAGE_RELEASED,
    }

    struct Order {
        ORDER_STATUS status;
        uint value;
        // address store_addr;
        // address storage_addr;
        // address delivery_addr;
        // address client_addr;

        mapping (bytes32 => address) addr;

        mapping (bytes32 => bool) confirm;
    }
    mapping (bytes32 => Order) orders;

    uint constant STORAGE_FEE = 1000;
    uint constant DELIVERY_FEE = 1000;

    modifier requireOrderParty(bytes32 order_id, PARTY_TYPE party) {
        require(orders[order_id].addr[sha3(party)] == msg.sender);
        _;
    }

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
    function client_place_order(bytes32 order_id, address client_addr) requireOrderStatus(order_id, ORDER_STATUS.DEFAULT) public payable {
        // require(msg.value >= ITEM_PRICE + STORAGE_FEE + DELIVERY_FEE);
        orders[order_id] = Order(ORDER_STATUS.PLACED, msg.value,
                {client_addr, 0, 0, msg.sender});
    }

    function confirm(bytes32 order_id, PARTY_TYPE party) requireParty(party) public {
        request(orders[order_id].confirm[sha3(party)] == false);
        orders[order_id].confirm[sha3(party)] = true;
        orders[order_id].addr[sha3(party)] = msg.sender;
    }

    function storage_receive(bytes32 order_id) requireOrderParty(order_id, PARTY_TYPE.STORAGE) requireOrderStatus(order_id, ORDER_STATUS.PLACED) public {
        orders[order_id].status = ORDER_STATUS.STORAGE_RECEIVED;
    }

    function storage_release(bytes32 order_id) requireOrderParty(order_id, PARTY_TYPE.STORAGE) requireOrderStatus(order_id, ORDER_STATUS.STORAGE_RECEIVED) public {
        orders[order_id].status = ORDER_STATUS.STORAGE_RELEASED;
    }

    function delivery_receive(bytes32 order_id) requireOrderParty(order_id, PARTY_TYPE.DELIVERY) requireOrderStatus(order_id, ORDER_STATUS.STORAGE_RELEASED) public {
        orders[order_id].status = ORDER_STATUS.DELIVERY_RECEIVED;
    }

    function delivery_release(bytes32 order_id) requireOrderParty(order_id, PARTY_TYPE.DELIVERY) requireOrderStatus(order_id, ORDER_STATUS.DELIVERY_RECEIVED) public {
        orders[order_id].status = ORDER_STATUS.DELIVERY_RELEASED;
    }

    function client_receive(bytes32 order_id) requireOrderParty(order_id, PARTY_TYPE.CLIENT) requireOrderStatus(order_id, ORDER_STATUS.DELIVERY_RELEASED) public {
        orders[order_id].status = ORDER_STATUS.CLIENT_RECEIVED;
    }


    // All the parties get payed
    function storage_withdraw_fee(bytes32 order_id) requireOrderParty(order_id, PARTY_TYPE.STORAGE) requireOrderStatus(order_id, ORDER_STATUS.CLIENT_RECEIVED) public {
        msg.sender.transfer(STORAGE_FEE);
        orders[order_id].addr[sha3(PARTY_TYPE.STORAGE)] = 0
    }

    function delivery_withdraw_fee(bytes32 order_id) requireOrderParty(order_id, PARTY_TYPE.DELIVERY) requireOrderStatus(order_id, ORDER_STATUS.CLIENT_RECEIVED) public {
        msg.sender.transfer(DELIVERY_FEE);
        orders[order_id].addr[sha3(PARTY_TYPE.DELIVERY)] = 0
    }

    function store_close_order(bytes32 order_id) requireOrderParty(order_id, PARTY_TYPE.STORE) requireOrderParty(order_id, PARTY_TYPE.DELIVERY) requireOrderStatus(order_id, ORDER_STATUS.CLIENT_RECEIVED) public {
        require(msg.sender == orders[order_id].store_addr);
        require(orders[order_id].addr[sha3(PARTY_TYPE.STORAGE)] == 0)
        require(orders[order_id].addr[sha3(PARTY_TYPE.DELIVERY)] == 0)

        msg.sender.transfer(orders[order_id].value - STORAGE_FEE - DELIVERY_FEE);

        delete orders[order_id];
    }

    function get_order_status(bytes32 order_id) constant public returns (ORDER_STATUS) {
        return orders[order_id].status;
    }

    function get_order_value(bytes32 order_id) constant public returns (uint) {
        return orders[order_id].value;
    }

}