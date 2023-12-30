import { ASTUtils } from "./ast-utils.js";

export class CHA {
  analyze(ast) {
    const classHierarchy = this.buildClassHierarchy(ast);
    return this.buildCallGraph(classHierarchy, ast);
  }

  buildClassHierarchy(ast) {
    const hierarchy = {};
    ast.nodes.forEach((node) => {
      if (node.nodeType === "ContractDefinition") {
        hierarchy[node.name] = {
          baseContracts: node.baseContracts.map((base) => base.baseName.name),
          functions: node.nodes
            .filter(
              (subNode) =>
                subNode.nodeType === "FunctionDefinition" &&
                subNode.kind !== "constructor"
            )
            .map((func) => func.name),
        };
      }
    });
    return hierarchy;
  }

  buildCallGraph(classHierarchy, ast) {
    const callGraph = {};
    Object.keys(classHierarchy).forEach((contractName) => {
      classHierarchy[contractName].functions.forEach((func) => {
        const funcKey = `${contractName}.${func}`;
        callGraph[funcKey] = this.analyzeFunction(
          ast,
          contractName,
          func,
          classHierarchy
        );
      });
    });
    return callGraph;
  }

  analyzeFunction(ast, contractName, func, classHierarchy) {
    const functionNode = ASTUtils.findFunctionNode(ast, contractName, func);
    const functionCalls = new Set();

    if (functionNode) {
      ASTUtils.findFunctionCalls(functionNode).forEach((calledFunc) => {
        ASTUtils.resolveFunctionCalls(calledFunc, classHierarchy).forEach(
          (targetFunc) => {
            functionCalls.add(targetFunc);
          }
        );
      });
    }

    return functionCalls;
  }
}
