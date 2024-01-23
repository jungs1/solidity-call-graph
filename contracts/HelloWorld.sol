// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Parent {
    string state_variable = "Hello World";

    function while_loop() public view returns (string memory) {
        uint256 j = 0;
        while (j < 10) {
            j++;
        }
    }

    function if_else() public view returns (string memory) {
        uint256 num = 100;

        if (true) {
            num = 3;
        } else {
            num = 10;
        }
    }

    function for_loop() public view returns (string memory) {
        uint256 num = 0;
        for (uint i = 0; i < 5; i++) {
            num = 10;
        }
    }

    function logic_short_circuit() public view returns (string memory) {
        uint256 num = 0;
        if (true || false) {
            num = 3;
        }
    }
}

contract ChildA is Parent {}

contract ChildB is Parent {}

contract ChildC is Parent {}

contract ChildD is Parent {}
