// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Parent {
    string state_variable = "Hello World";

    // function while_loop() public view returns (bool) {
    //     uint256 j = 0;
    //     while (j < 10) {
    //         j++;
    //     }
    //     j = 200;
    //     j += 12;
    //     return 43 != 2;
    // }

    function if_else() public view returns (bool) {
        uint256 num = 100;
        // if (3 < 3) {
        //     return false;
        // }
        if (true) {
            num = 3;
        } else {
            num = 10;
        }
        return true;
    }

    // function for_loop() public view returns (uint) {
    //     uint256 num = 0;
    //     for (uint i = 0; i < 5; i++) {
    //         num = 10;
    //     }
    //     num += 2;
    //     return 32;
    // }

    // function logic_short_circuit() public view returns (string memory) {
    //     uint256 num = 0;
    //     if (true || false) {
    //         num = 3;
    //     }
    //     num += 123;
    //     return "hi";
    // }
}

contract ChildA is Parent {}

contract ChildB is Parent {}

contract ChildC is Parent {}

contract ChildD is Parent {}
