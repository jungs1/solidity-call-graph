from src.analyzers.abstract_analyzer import AbstractAnalyzer
from src.analyzers.class_hierarchy_analyzer import ClassHierarchyAnalyzer
from graphviz import Digraph


class CallGraphAnalyzer(AbstractAnalyzer):
    def __init__(self, parser, class_hierarchy_analyzer):
        self.parser = parser
        self.class_hierarchy_analyzer = class_hierarchy_analyzer

    def analyze(self, algorithm):
        "algorithm CHA or RTA"
        class_hierarchy = self.class_hierarchy_analyzer.build_class_hierarchy(
            self.parser.ast
        )

        if algorithm == "RTA":
            instantiated_contracts = self.identify_instantiated_contracts(
                self.parser.ast
            )
            call_graph = self.build_rta_call_graph(
                class_hierarchy, instantiated_contracts, self.parser.ast
            )

        elif algorithm == "CHA":
            call_graph = self.build_cha_call_graph(class_hierarchy, self.parser.ast)
        else:
            raise ValueError("Invalid algorithm")
        self.visualize(call_graph, algorithm)

    def identify_instantiated_contracts(self, ast):
        instantiated_contracts = set()

        def traverse(node):
            if "nodeType" in node and node["nodeType"] == "NewExpression":
                contract_name = node.get("typeName").get("pathNode").get("name")
                if contract_name:
                    instantiated_contracts.add(contract_name)

            for key, value in node.items():
                if isinstance(value, dict):
                    traverse(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            traverse(item)

        traverse(ast)
        return instantiated_contracts

    def build_rta_call_graph(self, class_hierarchy, instantiated_contracts, ast):
        call_graph = {}
        for contract_name, contract_info in class_hierarchy.items():
            for func in contract_info["functions"]:
                func_key = f"{contract_name}.{func}"
                call_graph[func_key] = set()

                function_node = self.find_function_node(ast, contract_name, func)
                if function_node:
                    called_functions = self.find_function_calls(function_node)
                    for called_func in called_functions:
                        target_functions = self.resolve_function_calls(
                            called_func, class_hierarchy
                        )
                        for target_func in target_functions:
                            # Only add to the call graph if the target function's class is instantiated
                            target_class = target_func.split(".")[0]
                            if target_class in instantiated_contracts:
                                call_graph[func_key].add(target_func)

        return call_graph

    def build_cha_call_graph(self, class_hierarchy, ast):
        call_graph = {}
        for contract_name, contract_info in class_hierarchy.items():
            for func in contract_info["functions"]:
                func_key = f"{contract_name}.{func}"
                call_graph[func_key] = self.analyze_function(
                    ast, contract_name, func, class_hierarchy
                )
        return call_graph

    def visualize(self, call_graph, algorithm):
        dot = Digraph(comment="Call Graph Analysis")
        for func_key, func_calls in call_graph.items():
            dot.node(func_key, label=func_key)
            for called_func in func_calls:
                dot.edge(func_key, called_func)
        if algorithm == "RTA":
            filename = "call-graph-rta"
        elif algorithm == "CHA":
            filename = "call-graph-cha"
        else:
            raise ValueError("Invalid algorithm")
        dot.render(filename, format="png", cleanup=True)
        print(f"Call Graph using {algorithm} saved as cha.png")

    def resolve_function_calls(self, called_func, class_hierarchy):
        target_functions = set()

        for contract_name, contract_info in class_hierarchy.items():
            if called_func in contract_info["functions"]:
                target_functions.add(f"{contract_name}.{called_func}")

            for base_contract_name in contract_info["baseContracts"]:
                if called_func in class_hierarchy[base_contract_name]["functions"]:
                    target_functions.add(f"{base_contract_name}.{called_func}")

        return target_functions

    def analyze_function(self, ast, contract_name, func, class_hierarchy):
        function_node = self.find_function_node(ast, contract_name, func)
        function_calls = set()
        if function_node:
            for called_func in self.find_function_calls(function_node):
                for target_func in self.resolve_function_calls(
                    called_func, class_hierarchy
                ):
                    function_calls.add(target_func)

        return function_calls

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

    def get_function_call_name(self, function_call_node):
        if "expression" in function_call_node:
            if function_call_node["expression"]["nodeType"] == "Identifier":
                return function_call_node["expression"]["name"]
            elif function_call_node["expression"]["nodeType"] == "MemberAccess":
                return function_call_node["expression"]["memberName"]
        return None

    def find_function_calls(self, function_node):
        function_calls = []

        def traverse(node):
            function_name = self.get_function_call_name(node)
            if function_name:
                function_calls.append(function_name)

            for key, value in node.items():
                if isinstance(value, dict):
                    traverse(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            traverse(item)

        traverse(function_node)
        return function_calls
