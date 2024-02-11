// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Parent {
    string stateVar1 = "var1";
    string stateVar2 = "var1";

    function while_loop() public pure returns (bool) {
        uint256 j = 0;
        while (j < 10) {
            j++;
        }
        j = 200;
        j += 12;
        return 43 != 2;
    }

    // function functionA() public pure returns (bool) {
    //     uint256 cool_var1 = 100;
    //     cool_var1 = 23230;
    //     uint256 cool_var2 = 300;
    //     if (cool_var1 > 100) {
    //         cool_var1 = 3;
    //         cool_var1 = cool_var1;
    //         if (true) {
    //                 cool_var1 = 3;
    //         }
    //     } else if (cool_var1 < 100) {
    //         cool_var1 = 10;
    //     } else {
    //         cool_var1 = 10;
    //     }
    //     cool_var2 = 30;
    //     return true;
    // }

    // function for_loop() public pure returns (uint) {
    //     uint256 num = 0;
    //     for (uint i = 0; i < 5; i++) {
    //         num = 10;
    //     }
    //     num += 2;
    //     return 32;
    // }

    // function logic_short_circuit() public pure returns (string memory) {
    //     uint256 num = 0;
    //     if (true || false) {
    //         num = 3;
    //     }
    //     num += 123;
    //     return "hi";
    // }
}

// contract ChildA is Parent {}

// contract ChildB is Parent {}

// contract ChildC is Parent {}

// contract ChildD is Parent {}
