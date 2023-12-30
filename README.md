# Solidity CHA and RTA

This code offers implementations of Class Hierarchy Analysis (CHA) and Rapid Type Analysis (RTA) for Solidity smart contracts by analyzing the Abstract Syntax Tree (AST) of Solidity contracts. It's important to note that these are not full implementations but rather simplified versions designed for exploration and educational purposes. They serve as a practical guide for those looking to understand how CHA and RTA work in the context of Solidity and to experiment with these analysis techniques in a more controlled environment.

## Prerequisites

- Solidity Compiler (solc) version 0.8.24
- Node.js version 20.10.0

## Compiling Solidity Contracts

Use the following command to compile Solidity contracts and generate the required artifacts:

```bash
solc -o output --bin --ast-compact-json --asm contracts/example.sol
```

# CHA and RTA in Action: A Solidity Example

CHA and RTA are analysis methodologies to generate call graphs.
Consider a Solidity system with several contracts: `IToken`, `Bitcoin`, `Ethereum`, `TokenFactory`, and `Wallet`. `Bitcoin` and `Ethereum` implement the `IToken` interface. `Wallet` interacts with an `IToken`, and `TokenFactory` dynamically creates instances of `Bitcoin` or `Ethereum`.

```solidity
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
```

### CHA Analysis Result

```js
{
  'IToken.transfer': Set(0) {},
  'Bitcoin.transfer': Set(0) {},
  'Ethereum.transfer': Set(0) {},
  'TokenFactory.createToken': Set(0) {},
  'Wallet.makeTransfer': Set(3) { 'IToken.transfer', 'Bitcoin.transfer', 'Ethereum.transfer' },
  'Wallet.changeToken': Set(0) {}
}

```

## RTA Analysis Result

```js
{
  'IToken.transfer': Set(0) {},
  'Bitcoin.transfer': Set(0) {},
  'Ethereum.transfer': Set(0) {},
  'TokenFactory.createToken': Set(0) {},
  'Wallet.makeTransfer': Set(2) { 'Bitcoin.transfer', 'Ethereum.transfer' },
  'Wallet.changeToken': Set(0) {}
}

```

CHA is known for its **soundness**, covering all possible interactions, including paths not executed at runtime. This comprehensive approach, however, may introduce complexity by including non-executed paths.

In contrast, RTA is valued for its **precision**, focusing on instantiated contracts for a more targeted and practical analysis. While offering a concise view, it might miss interactions involving non-instantiated contracts. The choice between CHA's comprehensive coverage and RTA's focused analysis depends on the specific needs of the analysis, whether it be a complete overview or an assessment of probable runtime behavior.
