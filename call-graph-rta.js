import { CHA } from "./call-graph-cha.js";
import { ASTUtils } from "./ast-utils.js";

export class RTA {
  constructor() {
    this.cha = new CHA();
    this.instantiatedClasses = new Set();
  }

  analyze(ast) {
    const classHierarchy = this.cha.buildClassHierarchy(ast);
    this.identifyInstantiatedClasses(ast);
    return this.buildInstantiatedCallGraph(classHierarchy, ast);
  }

  identifyInstantiatedClasses(ast) {
    ASTUtils.traverseAST(ast, (node) => {
      if (
        node.nodeType === "NewExpression" &&
        node.typeName &&
        node.typeName.pathNode
      ) {
        this.instantiatedClasses.add(node.typeName.pathNode.name);
      }
    });
  }

  buildInstantiatedCallGraph(classHierarchy, ast) {
    const callGraph = {};
    Object.keys(classHierarchy).forEach((contractName) => {
      classHierarchy[contractName].functions.forEach((func) => {
        const funcKey = `${contractName}.${func}`;
        callGraph[funcKey] = new Set();

        const functionNode = ASTUtils.findFunctionNode(ast, contractName, func);
        if (functionNode) {
          const calledFunctions = ASTUtils.findFunctionCalls(functionNode);
          calledFunctions.forEach((calledFunc) => {
            const targetFunctions = ASTUtils.resolveFunctionCalls(
              calledFunc,
              classHierarchy,
              contractName
            );
            targetFunctions.forEach((targetFunc) => {
              // Only add to the call graph if the target function's class is instantiated
              const targetClass = targetFunc.split(".")[0];
              if (this.instantiatedClasses.has(targetClass)) {
                callGraph[funcKey].add(targetFunc);
              }
            });
          });
        }
      });
    });
    return callGraph;
  }
}
