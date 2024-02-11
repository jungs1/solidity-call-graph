from src.analyzers.abstract_analyzer import AbstractAnalyzer
from graphviz import Digraph
from src.parsers.nodes import ASTNode, ContractDefinition, FunctionDefinition


class ClassHierarchyAnalyzer(AbstractAnalyzer):
    def __init__(self, parser):
        self.parser = parser

    def visualize(self, class_hierarchy):
        dot = Digraph(comment="Class Hierarchy Analysis")
        for contract, funcs in class_hierarchy.items():
            for base in funcs["baseContracts"]:
                dot.node(base, label=base)
                dot.edge(base, contract)
            dot.node(contract, label=contract)

        dot.render("cha", format="png", cleanup=True)
        print(f"CHA saved as cha.png")

    def analyze(self):
        class_hierarchy = self.build_class_hierarchy(self.parser.ast_v2)
        self.visualize(class_hierarchy)

    def build_class_hierarchy(self, ast):
        hierarchy = {}
        for node in ast.nodes:
            if type(node) == ContractDefinition:
                hierarchy[node.name] = {"baseContracts": [], "functions": []}
                for base_contracts in node.baseContracts:
                    hierarchy[node.name]["baseContracts"].append(
                        base_contracts["baseName"]["name"]
                    )
                for inner_node in node.nodes:
                    if type(inner_node) == FunctionDefinition:
                        hierarchy[node.name]["functions"].append(inner_node.name)

        return hierarchy

    def traverse_ast(self, ast, callback):
        def traverse(node):
            callback(node)
            for key, value in node.items():
                if isinstance(value, dict):
                    traverse(value)

        traverse(ast)
