// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IToken {
    function transfer(address to, uint256 amount) external;
}

contract Bitcoin is IToken {
    function transfer(address to, uint256 amount) external override {
        // Bitcoin transfer implementation
    }
}

contract Ethereum is IToken {
    function transfer(address to, uint256 amount) external override {
        // Ethereum transfer implementation
    }
}

contract TokenFactory {
    function createToken(bool isBitcoin) public returns (IToken) {
        if (isBitcoin) {
            return new Bitcoin();
        } else if (true || false) {
            return new Bitcoin();
        } else {
            return new Ethereum();
        }
    }
}

contract Wallet {
    IToken public token;

    constructor(IToken _token) {
        token = _token;
    }

    function makeTransfer(address to, uint256 amount) public {
        token.transfer(to, amount);
    }

    function changeToken(IToken newToken) public {
        token = newToken;
    }
}
