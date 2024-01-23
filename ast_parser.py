from control_flow_graph import ControlFlowGraph

from graphviz import Digraph


class AnalysisModule:
    def analyze(self):
        raise NotImplementedError


class ControlFlowGraphAnalyzer(AnalysisModule):
    def __init__(self, ast_parser):
        self.ast_parser = ast_parser
        self.cfg = ControlFlowGraph()

    def _format_node_label(self, node):
        """Format the label for a node."""
        node_desc = node.node_type
        statements = "\n".join(node.statements)
        return f"{node_desc}\n{statements}"

    def visualize(self, filename="cfg"):
        dot = Digraph(comment="Control Flow Graph")
        node_colors = {
            "FunctionEntry": "lightblue",
            "FunctionExit": "lightblue",
            "IfStatement": "yellow",
            "IfStatement Convergent": "yellow",
            "WhileCondition": "orange",
            "WhileBody": "orange",
            "AfterWhile": "orange",
            "ForInit": "green",
            "ForCondition": "green",
            "ForBody": "green",
            "AfterFor": "green",
            "ForIncrement": "green",
        }
        # Add nodes to the graph
        for node_id, node in self.cfg.nodes.items():
            label = self._format_node_label(node)
            color = node_colors.get(node.node_type, "white")

            dot.node(node_id, label, style="filled", fillcolor=color)

        # Add edges to the graph
        for node_id, node in self.cfg.nodes.items():
            for target_node, annotation in node.outgoing_edges:
                edge_attrs = {}
                if annotation:
                    edge_attrs["label"] = str(annotation)
                edge_attrs["color"] = "red"
                dot.edge(node_id, target_node.node_id, **edge_attrs)

        # Render the graph to a file
        dot.render(filename, format="png", cleanup=True)
        print(f"CFG saved as {filename}.png")

    def analyze(self):
        self.parse()
        self.visualize()

    def get_source_snippet(self, src):
        start, length = map(int, src.split(":")[:2])
        return self.ast_parser.source_code[start : start + length]

    def parse(self):
        for node in self.ast_parser.ast["nodes"]:
            if node["nodeType"] == "ContractDefinition":
                self.parse_contract(node)

    def parse_contract(self, contract_node):
        for node in contract_node["nodes"]:
            if node["nodeType"] == "FunctionDefinition":
                self.parse_function(node)

    def parse_function(self, function_node):
        entry_node, exit_node = self.cfg.add_function_entry_exit(
            function_id=function_node["id"],
            function_name=function_node["name"],
        )
        # Parse the body of the function
        body_node = function_node.get("body")
        if body_node:
            end_node = self.parse_block(body_node, entry_node)
        self.cfg.connect_nodes(end_node, exit_node)

    def parse_block(self, block_node, parent_node):
        prev_node = parent_node
        for statement in block_node["statements"]:
            if statement["nodeType"] == "VariableDeclarationStatement":
                prev_node = self.parse_variable_declaration(statement, prev_node)
            elif statement["nodeType"] == "ExpressionStatement":
                prev_node = self.parse_expression_statement(statement, prev_node)
            elif statement["nodeType"] == "IfStatement":
                prev_node = self.parse_if_statement(statement, prev_node)
            elif statement["nodeType"] == "ForStatement":
                prev_node = self.parse_for_loop(statement, prev_node)
            elif statement["nodeType"] == "WhileStatement":
                prev_node = self.parse_while_loop(statement, prev_node)
            else:
                None
        return prev_node

    def parse_variable_declaration(self, var_decl_node, parent_node):
        code_snippet = self.get_source_snippet(var_decl_node["src"])
        parent_node.add_statement(f"Declare: {code_snippet}")
        return parent_node

    def parse_expression_statement(self, expr_stmt_node, parent_node):
        code_snippet = self.get_source_snippet(expr_stmt_node["src"])
        parent_node.add_statement(f"Expr: {code_snippet}")
        return parent_node

    def parse_if_statement(self, if_node, parent_node):
        # Evaluate the condition
        # Par
        if if_node["condition"]["nodeType"] == "BinaryOperation":
            condition_node = self.parse_logical_expression(
                if_node["condition"], parent_node
            )
            parent_node = condition_node
        if_condition_code = self.get_source_snippet(if_node["condition"]["src"])

        if_statement_node = self.cfg.add_node(
            node_id=if_node["id"], node_type=if_node["nodeType"]
        )
        convergent_node = self.cfg.add_node(
            f"convergent_ {if_node['id']}", f"{if_node['nodeType']} Convergent"
        )
        if_statement_node.add_statement(f"If: {if_condition_code}")

        self.cfg.connect_nodes(
            parent_node,
            if_statement_node,
            annotation=f"Condition: {self.get_source_snippet(if_node['src'])}",
        )

        # Process the true body
        if "trueBody" in if_node:
            true_branch_node = self.cfg.add_node(
                node_id=f"{if_node['id']}_true", node_type=if_node["nodeType"]
            )
            self.cfg.connect_nodes(
                if_statement_node, true_branch_node, annotation=f"True"
            )
            self.parse_block(if_node["trueBody"], true_branch_node)
            self.cfg.connect_nodes(true_branch_node, convergent_node)
        # Process the false body
        if "falseBody" in if_node:
            false_branch_node = self.cfg.add_node(
                node_id=f"{if_node['id']}_false", node_type=if_node["nodeType"]
            )
            self.cfg.connect_nodes(
                if_statement_node, false_branch_node, annotation=f"False"
            )
            self.parse_block(if_node["falseBody"], false_branch_node)
            self.cfg.connect_nodes(
                false_branch_node,
                convergent_node,
            )

        return convergent_node

    def add_statement_to_cfg_node(self, stmt_ast, cfg_node):
        # This method adds a statement from the AST to the CFG node
        # It could be a variable declaration, assignment, etc.
        if stmt_ast["nodeType"] == "VariableDeclarationStatement":
            # Handle variable declaration
            # Extract relevant information from stmt_ast and add it to cfg_node
            cfg_node.add_statement(f"Declare: {stmt_ast['src']}")
        elif stmt_ast["nodeType"] == "ExpressionStatement":
            # Handle expression statement (like an assignment)
            # Extract relevant information from stmt_ast and add it to cfg_node
            cfg_node.add_statement(f"Expr: {stmt_ast['src']}")

    def parse_for_loop(self, for_node, parent_node):
        def process_for_init(init_ast, init_node_cfg):
            var_name = init_ast["declarations"][0]["name"]
            init_value = init_ast["initialValue"]["value"]
            init_node_cfg.add_statement(f"{var_name} = {init_value}")

        def process_for_condition(condition_ast, condition_node_cfg):
            # Process loop condition
            left_expr = condition_ast["leftExpression"]["name"]
            right_expr = condition_ast["rightExpression"]["value"]
            operator = condition_ast["operator"]
            condition_node_cfg.add_statement(f"{left_expr} {operator} {right_expr}")

        def process_for_increment(increment_ast, increment_node_cfg):
            # Add the increment expression to the CFG node
            # Example: "i++"
            var_name = increment_ast["expression"]["subExpression"]["name"]
            operator = increment_ast["expression"]["operator"]
            increment_node_cfg.add_statement(f"{var_name}{operator}")

        # Create a node for the initialization
        init_node = self.cfg.add_node(
            node_id=f"{for_node['id']}_init", node_type="ForInit"
        )
        self.cfg.connect_nodes(parent_node, init_node)

        # Assuming you have a method to process the initialization part
        process_for_init(for_node["initializationExpression"], init_node)

        # Create a node for the loop condition
        loop_condition_node = self.cfg.add_node(
            node_id=f"{for_node['id']}_condition", node_type="ForCondition"
        )
        self.cfg.connect_nodes(init_node, loop_condition_node)

        # # Assuming you have a method to process the condition part
        process_for_condition(for_node["condition"], loop_condition_node)

        # Create a node for the body of the loop
        loop_body_node = self.cfg.add_node(
            node_id=f"{for_node['id']}_body", node_type="ForBody"
        )
        self.cfg.connect_nodes(loop_condition_node, loop_body_node)

        # Parse the body of the loop
        self.parse_block(for_node["body"], loop_body_node)

        # Create a node for the increment/update part of the loop
        increment_node = self.cfg.add_node(
            node_id=f"{for_node['id']}_increment", node_type="ForIncrement"
        )
        self.cfg.connect_nodes(loop_body_node, increment_node)

        # Assuming you have a method to process the increment part
        process_for_increment(for_node["loopExpression"], increment_node)

        # Create a back edge from the increment to the condition
        self.cfg.connect_nodes(increment_node, loop_condition_node)

        # Create a node for after the loop
        after_loop_node = self.cfg.add_node(
            node_id=f"{for_node['id']}_after", node_type="AfterFor"
        )
        self.cfg.connect_nodes(loop_condition_node, after_loop_node)

        return after_loop_node

    def parse_while_loop(self, while_node, parent_node):
        # Create a node for the loop condition
        loop_condition_node = self.cfg.add_node(
            node_id=f"{while_node['id']}_condition", node_type="WhileCondition"
        )
        self.cfg.connect_nodes(parent_node, loop_condition_node)

        # Create a node for the body of the loop
        loop_body_node = self.cfg.add_node(
            node_id=f"{while_node['id']}_body", node_type="WhileBody"
        )
        self.cfg.connect_nodes(loop_condition_node, loop_body_node)

        # Parse the body of the loop
        self.parse_block(while_node["body"], loop_body_node)

        # Create a back edge from the body to the condition (for repeating the loop)
        self.cfg.connect_nodes(loop_body_node, loop_condition_node)

        # Create a node for after the loop
        after_loop_node = self.cfg.add_node(
            node_id=f"{while_node['id']}_after", node_type="AfterWhile"
        )
        self.cfg.connect_nodes(loop_condition_node, after_loop_node)

        return after_loop_node

    def process_expression(self, expr_ast, cfg_node):
        # Determine the type of expression and handle accordingly
        if expr_ast["nodeType"] == "Literal":
            self.process_literal(expr_ast, cfg_node)
        elif expr_ast["nodeType"] == "BinaryOperation":
            self.process_binary_operation(expr_ast, cfg_node)
        elif expr_ast["nodeType"] == "UnaryOperation":
            self.process_unary_operation(expr_ast, cfg_node)
        elif expr_ast["nodeType"] == "Identifier":
            self.process_identifier(expr_ast, cfg_node)
        elif expr_ast["nodeType"] == "FunctionCall":
            self.process_function_call(expr_ast, cfg_node)
        # ... other expression types ...

    def process_literal(self, literal_ast, cfg_node):
        code_snippet = self.get_source_snippet(literal_ast["src"])
        cfg_node.add_statement(f"Literal: {code_snippet}")

    def process_binary_operation(self, binary_op_ast, cfg_node):
        code_snippet = self.get_source_snippet(binary_op_ast["src"])
        cfg_node.add_statement(f"Binary Operation: {code_snippet}")

    def process_unary_operation(self, unary_op_ast, cfg_node):
        # Handle unary operations (e.g., -, !)
        operand = unary_op_ast["subExpression"]
        operator = unary_op_ast["operator"]
        cfg_node.add_statement(f"Unary Operation: {operator}{operand['src']}")

    def process_identifier(self, identifier_ast, cfg_node):
        # Handle identifiers (variable names, etc.)
        name = identifier_ast["name"]
        cfg_node.add_statement(f"Identifier: {name}")

    def process_function_call(self, func_call_ast, cfg_node):
        # Handle function calls
        func_name = func_call_ast["expression"]["name"]  # Simplified; adjust as needed
        cfg_node.add_statement(f"Function Call: {func_name}()")

    def parse_logical_expression(self, logical_expr_ast, parent_node):
        # Assuming logical_expr_ast is the AST node for "A || B" or "A && B"
        left_operand = logical_expr_ast["leftExpression"]
        right_operand = logical_expr_ast["rightExpression"]
        operator = logical_expr_ast["operator"]

        # Create nodes for evaluating left and right operands
        left_node = self.cfg.add_node(
            f"{left_operand['id']}_left", left_operand["nodeType"]
        )
        left_node_code_snippet = self.get_source_snippet(left_operand["src"])
        left_node.add_statement(f"Evaluate left operand: {left_node_code_snippet}")

        right_node = self.cfg.add_node(
            f"{right_operand['id']}_right", right_operand["nodeType"]
        )
        right_node_code_snippet = self.get_source_snippet(right_operand["src"])
        right_node.add_statement(f"Evaluate right operand: {right_node_code_snippet}")

        # Connect the parent node to the left operand node
        self.cfg.connect_nodes(parent_node, left_node)
        # Evaluate the left operand
        self.process_expression(left_operand, left_node)
        # Logic for short-circuiting
        if operator == "||":
            # For "||", if left is true, skip right operand
            bypass_node = self.cfg.add_node(
                f"{logical_expr_ast['id']}_bypass", "Bypass"
            )
            self.cfg.connect_nodes(left_node, bypass_node, annotation="True")
            self.cfg.connect_nodes(
                left_node,
                right_node,
                annotation="False",
            )
        elif operator == "&&":
            pass

        # Evaluate the right operand (if not bypassed)
        self.process_expression(right_operand, right_node)

        convergent_node = self.cfg.add_node(
            f"{logical_expr_ast['id']}_convergent",
            f"{logical_expr_ast['nodeType']} Convergent",
        )
        # Connect the left and right nodes to the convergent node
        self.cfg.connect_nodes(bypass_node, convergent_node)
        self.cfg.connect_nodes(right_node, convergent_node)

        return convergent_node


class ClassHierarchyAnalyzer(AnalysisModule):
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


class CallGraphAnalyzer(AnalysisModule):
    def __init__(self, ast_parser, call_graph_type="CHA"):
        self.ast_parser = ast_parser
        self.class_hierarchy_analyzer = ClassHierarchyAnalyzer(ast_parser)
        self.call_graph_type = call_graph_type  # CHA or RTA

    def analyze(self):
        class_hierarchy = self.class_hierarchy_analyzer.build_class_hierarchy(
            self.ast_parser.ast
        )

        if self.call_graph_type == "RTA":
            instantiated_contracts = self.identify_instantiated_contracts(
                self.ast_parser.ast
            )
            call_graph = self.build_rta_call_graph(
                class_hierarchy, instantiated_contracts, self.ast_parser.ast
            )

        else:
            call_graph = self.build_cha_call_graph(class_hierarchy, self.ast_parser.ast)
        self.visualize(call_graph)

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

    def visualize(self, call_graph):
        dot = Digraph(comment="Call Graph Analysis")
        for func_key, func_calls in call_graph.items():
            dot.node(func_key, label=func_key)
            for called_func in func_calls:
                dot.edge(func_key, called_func)
        if self.call_graph_type == "RTA":
            filename = "call-graph-rta"
        else:
            filename = "call-graph-cha"
        dot.render(filename, format="png", cleanup=True)
        print(f"Call Graph using {self.call_graph_type} saved as cha.png")

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


class ASTParser:
    def __init__(self, ast, source_code):
        self.ast = ast
        self.source_code = source_code
        self.class_hierarchy_analyzer = ClassHierarchyAnalyzer(self)
        self.control_flow_graph_analyzer = ControlFlowGraphAnalyzer(self)
        self.call_graph_analyzer = CallGraphAnalyzer(self)
