from src.analyzers.abstract_analyzer import AbstractAnalyzer
from graphviz import Digraph


class ClassHierarchyAnalyzer(AbstractAnalyzer):
    def __init__(self, ast_parser):
        self.ast_parser = ast_parser

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
        class_hierarchy = self.build_class_hierarchy(self.ast_parser.ast)
        self.visualize(class_hierarchy)

    def build_class_hierarchy(self, ast):
        hierarchy = {}
        for node in ast["nodes"]:
            if node["nodeType"] == "ContractDefinition":
                hierarchy[node["name"]] = {
                    "baseContracts": [
                        base["baseName"]["name"] for base in node["baseContracts"]
                    ],
                    "functions": [
                        func["name"]
                        for func in node["nodes"]
                        if func["nodeType"] == "FunctionDefinition"
                        and func["kind"] != "constructor"
                    ],
                }
        return hierarchy

    def find_function_node(self, ast, contract_name, function_name):
        for node in ast["nodes"]:
            if (
                node["nodeType"] == "ContractDefinition"
                and node["name"] == contract_name
            ):
                for sub_node in node["nodes"]:
                    if (
                        sub_node["nodeType"] == "FunctionDefinition"
                        and sub_node["name"] == function_name
                    ):
                        return sub_node
        return None

    def find_function_calls(self, function_node):
        function_calls = []

        def traverse(node):
            if node["nodeType"] == "FunctionCall":
                function_name = self.get_function_call_name(node)
                if function_name:
                    function_calls.append(function_name)

            for key, value in node.items():
                if isinstance(value, dict):
                    traverse(value)

        traverse(function_node)
        return function_calls

    def get_function_call_name(self, function_call_node):
        if "expression" in function_call_node:
            if function_call_node["expression"]["nodeType"] == "Identifier":
                return function_call_node["expression"]["name"]
            elif function_call_node["expression"]["nodeType"] == "MemberAccess":
                return function_call_node["expression"]["memberName"]
        return None

    def resolve_function_calls(self, called_func, class_hierarchy):
        target_functions = set()

        for contract_name, contract_info in class_hierarchy.items():
            if called_func in contract_info["functions"]:
                target_functions.add(f"{contract_name}.{called_func}")

            for base_contract_name in contract_info["baseContracts"]:
                if called_func in class_hierarchy[base_contract_name]["functions"]:
                    target_functions.add(f"{base_contract_name}.{called_func}")

        return target_functions

    def traverse_ast(self, ast, callback):
        def traverse(node):
            callback(node)
            for key, value in node.items():
                if isinstance(value, dict):
                    traverse(value)

        traverse(ast)
