export class ASTUtils {
  static findFunctionNode(ast, contractName, functionName) {
    for (const node of ast.nodes) {
      if (
        node.nodeType === "ContractDefinition" &&
        node.name === contractName
      ) {
        for (const subNode of node.nodes) {
          if (
            subNode.nodeType === "FunctionDefinition" &&
            subNode.name === functionName
          ) {
            return subNode;
          }
        }
      }
    }
    return null;
  }

  static findFunctionCalls(functionNode) {
    const functionCalls = [];

    const traverse = (node) => {
      if (node.nodeType === "FunctionCall") {
        const functionName = this.getFunctionCallName(node);
        if (functionName) {
          functionCalls.push(functionName);
        }
      }

      for (const key in node) {
        if (node.hasOwnProperty(key) && typeof node[key] === "object") {
          traverse(node[key]);
        }
      }
    };
    traverse(functionNode);
    return functionCalls;
  }

  static getFunctionCallName(functionCallNode) {
    if (
      functionCallNode.expression &&
      functionCallNode.expression.nodeType === "Identifier"
    ) {
      return functionCallNode.expression.name;
    }

    if (
      functionCallNode.expression &&
      functionCallNode.expression.nodeType === "MemberAccess"
    ) {
      return functionCallNode.expression.memberName;
    }

    return null;
  }

  static resolveFunctionCalls(calledFunc, classHierarchy) {
    let targetFunctions = new Set();

    Object.keys(classHierarchy).forEach((contractName) => {
      const contractInfo = classHierarchy[contractName];

      if (contractInfo.functions.includes(calledFunc)) {
        targetFunctions.add(`${contractName}.${calledFunc}`);
      }

      contractInfo.baseContracts.forEach((baseContractName) => {
        if (classHierarchy[baseContractName].functions.includes(calledFunc)) {
          targetFunctions.add(`${baseContractName}.${calledFunc}`);
        }
      });
    });

    return targetFunctions;
  }

  static traverseAST(ast, callback) {
    const traverse = (node) => {
      callback(node);

      for (const key in node) {
        if (node.hasOwnProperty(key) && typeof node[key] === "object") {
          traverse(node[key]);
        }
      }
    };
    traverse(ast);
  }
}
