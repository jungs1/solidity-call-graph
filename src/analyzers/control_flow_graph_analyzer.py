from src.analyzers.abstract_analyzer import AbstractAnalyzer
from graphviz import Digraph
from typing import Dict, Tuple, Optional, List


class Statement:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text


class FunctionCallStatement(Statement):
    def __init__(self, function_name: str, arguments: list):
        self.function_name = function_name
        self.arguments = arguments
        arg_str = ", ".join(str(arg) for arg in arguments)
        text = f"{function_name}({arg_str})"
        super().__init__(text)


class VariableDeclarationStatement(Statement):
    def __init__(
        self, variable_name: str, variable_type: str, initial_value: str = None
    ):
        self.variable_name = variable_name
        self.variable_type = variable_type
        self.initial_value = initial_value
        text = f"{variable_type} {variable_name}"
        if initial_value is not None:
            text += f" = {initial_value}"
        super().__init__(text)


"""
An expression is a combination of one or more values, variables, operators, and function calls that the programming language interprets (according to its particular rules of precedence and of association) and computes to produce ("to return", in a stateful environment) another value. This means that expressions always produce or return a value.

"""


class ExpressionStatement(Statement):
    def __init__(self, expression: str):
        super().__init__(expression)


class CFGNode:
    """Represents a node in the Control Flow Graph."""

    def __init__(self, node_id, node_type):
        self.node_id: str = node_id
        self.node_type: str = node_type
        self.statements: List[str] = []
        self.incoming_edges: List[Tuple["CFGNode", Optional[str]]] = []
        self.outgoing_edges: List[Tuple["CFGNode", Optional[str]]] = []
        self.definitions = set()  # Store variable definitions made in this node

    def add_statement(self, statement):
        """Add a statement to the node's list of statements."""
        self.statements.append(statement)

    def add_definition(self, variable_name):
        """Add a variable definition to the node."""
        self.definitions.add(variable_name)

    def add_incoming_edge(self, node, annotation=None):
        """Add an incoming edge to the node."""
        self.incoming_edges.append((node, annotation))

    def add_outgoing_edge(self, node, annotation=None):
        """Add an outgoing edge to the node."""
        self.outgoing_edges.append((node, annotation))


class ControlFlowGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, CFGNode] = {}
        self.function_nodes: Dict[str, Tuple[CFGNode, CFGNode]] = {}

    def add_node(self, node_id: str, node_type: str) -> CFGNode:
        """Add a new node to the control flow graph."""
        if type(node_id) == int:
            node_id = str(node_id)
        node = CFGNode(node_id=node_id, node_type=node_type)
        self.nodes[node_id] = node
        return node

    def add_function_entry_exit(
        self, function_id: str, function_name: str
    ) -> Tuple[CFGNode, CFGNode]:
        """Create entry and exit nodes for a function."""
        entry_node = self.add_node(
            f"entry_{function_id}_{function_name}", "FunctionEntry"
        )
        exit_node = self.add_node(f"exit_{function_id}_{function_name}", "FunctionExit")
        self.function_nodes[f"{function_id}_{function_name}"] = (entry_node, exit_node)
        return entry_node, exit_node

    def connect_nodes(
        self, from_node: CFGNode, to_node: CFGNode, annotation: Optional[str] = None
    ) -> None:
        """Connect two nodes in the control flow graph."""
        from_node.add_outgoing_edge(to_node, annotation)
        to_node.add_incoming_edge(from_node, annotation)


class ControlFlowGraphAnalyzer(AbstractAnalyzer):
    def __init__(self, parser):
        self.parser = parser
        self.cfg = ControlFlowGraph()

    def _format_node_label(self, node):
        """Format the label for a node."""
        node_id = node.node_id
        node_type = node.node_type
        statements = []
        for statement in node.statements:
            statements.append(str(statement))
        statements = "\n".join(statements)
        return f"ID: {node_id}\nNODE_TYPE: {node_type}\nSTATEMENTS: {statements}"

    def visualize(self, filename="cfg"):
        dot = Digraph(comment="Control Flow Graph")
        node_colors = {
            "FunctionEntry": "lightblue",
            "FunctionExit": "lightblue",
            "IfStatement": "orange",
            "WhileStatement": "orange",
            "ForStatement": "orange",
            "BinaryOperation": "orange",
            "Return": "lightgreen",
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

    def parse(self):
        for node in self.parser.ast["nodes"]:
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
            end_node = self.parse_block(body_node, entry_node, exit_node)
            self.cfg.connect_nodes(end_node, exit_node)

    def parse_block(self, block_node, parent_node, exit_node=None):
        """
        Parses a block of code and updates the control flow graph accordingly.

        A block consists of a sequence of statements, which may include variable declarations,
        expression statements, and control flow elements like if statements and loops.
        This method iterates through each statement in the block and delegates to the appropriate
        parsing method based on the statement's node type.
        """
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
            elif statement["nodeType"] == "Return":
                prev_node = self.parse_return_statement(statement, prev_node)
            else:
                None
        return prev_node

    def parse_variable_declaration(
        self, var_decl_node: dict, parent_node: CFGNode
    ) -> None:
        variable_name = var_decl_node["declarations"][0]["name"]
        variable_type = var_decl_node["declarations"][0]["typeName"]["name"]
        initial_value = var_decl_node.get("initialValue", {}).get("value")
        statement = VariableDeclarationStatement(
            variable_name, variable_type, initial_value
        )
        parent_node.add_statement(statement)
        parent_node.add_definition(variable_name)
        return parent_node

    def parse_expression_statement(self, expr_stmt_node, parent_node):
        expression = self.parse_expression(expr_stmt_node["expression"])
        statement = ExpressionStatement(expression)
        parent_node.add_statement(statement)
        return parent_node

    def parse_expression(self, expr_node: dict) -> str:
        """
        Parses an expression AST node and returns its string representation.
        """
        if expr_node["nodeType"] == "BinaryOperation":
            # Parse the left and right expressions of the binary operation
            left_expr = self.parse_expression(expr_node["leftExpression"])
            right_expr = self.parse_expression(expr_node["rightExpression"])
            # Get the operator
            operator = expr_node["operator"]
            # Combine the left expression, operator, and right expression
            return f"{left_expr} {operator} {right_expr}"
        if expr_node["nodeType"] == "UnaryOperation":
            operator = expr_node["operator"]
            operand = self.parse_expression(expr_node["subExpression"])
            return f"{operator}{operand}"
        if expr_node["nodeType"] == "Assignment":
            # Parse the left-hand side (Identifier)
            left_hand_side = expr_node["leftHandSide"]["name"]
            # Parse the right-hand side, which could be a Literal or another type of expression
            right_hand_side = self.parse_expression(expr_node["rightHandSide"])
            # Get the operator
            operator = expr_node["operator"]
            # Construct the assignment expression string
            return f"{left_hand_side} {operator} {right_hand_side}"
        elif expr_node["nodeType"] == "Literal":
            # Directly return the literal value
            return expr_node["value"]
        elif expr_node["nodeType"] == "Identifier":
            # Directly return the identifier name
            return expr_node["name"]
        # Add more cases to handle different types of expressions as needed
        return "expression_placeholder"

    def parse_if_statement(self, if_node, parent_node):
        if if_node["condition"]["nodeType"] == "BinaryOperation":
            condition_node = self.parse_logical_expression(
                if_node["condition"], parent_node
            )
            parent_node = condition_node

        print("if node , if", if_node)
        temp = {
            "condition": {
                "hexValue": "74727565",
                "id": 13,
                "isConstant": False,
                "isLValue": False,
                "isPure": True,
                "kind": "bool",
                "lValueRequested": False,
                "nodeType": "Literal",
                "src": "433:4:0",
                "typeDescriptions": {"typeIdentifier": "t_bool", "typeString": "bool"},
                "value": "true",
            },
            "falseBody": {
                "id": 23,
                "nodeType": "Block",
                "src": "477:33:0",
                "statements": [
                    {
                        "expression": {
                            "id": 21,
                            "isConstant": False,
                            "isLValue": False,
                            "isPure": False,
                            "lValueRequested": False,
                            "leftHandSide": {
                                "id": 19,
                                "name": "num",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 10,
                                "src": "491:3:0",
                                "typeDescriptions": {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256",
                                },
                            },
                            "nodeType": "Assignment",
                            "operator": "=",
                            "rightHandSide": {
                                "hexValue": "3130",
                                "id": 20,
                                "isConstant": False,
                                "isLValue": False,
                                "isPure": True,
                                "kind": "number",
                                "lValueRequested": False,
                                "nodeType": "Literal",
                                "src": "497:2:0",
                                "typeDescriptions": {
                                    "typeIdentifier": "t_rational_10_by_1",
                                    "typeString": "int_const 10",
                                },
                                "value": "10",
                            },
                            "src": "491:8:0",
                            "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256",
                            },
                        },
                        "id": 22,
                        "nodeType": "ExpressionStatement",
                        "src": "491:8:0",
                    }
                ],
            },
            "id": 24,
            "nodeType": "IfStatement",
            "src": "429:81:0",
            "trueBody": {
                "id": 18,
                "nodeType": "Block",
                "src": "439:32:0",
                "statements": [
                    {
                        "expression": {
                            "id": 16,
                            "isConstant": False,
                            "isLValue": False,
                            "isPure": False,
                            "lValueRequested": False,
                            "leftHandSide": {
                                "id": 14,
                                "name": "num",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 10,
                                "src": "453:3:0",
                                "typeDescriptions": {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256",
                                },
                            },
                            "nodeType": "Assignment",
                            "operator": "=",
                            "rightHandSide": {
                                "hexValue": "33",
                                "id": 15,
                                "isConstant": False,
                                "isLValue": False,
                                "isPure": True,
                                "kind": "number",
                                "lValueRequested": False,
                                "nodeType": "Literal",
                                "src": "459:1:0",
                                "typeDescriptions": {
                                    "typeIdentifier": "t_rational_3_by_1",
                                    "typeString": "int_const 3",
                                },
                                "value": "3",
                            },
                            "src": "453:7:0",
                            "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256",
                            },
                        },
                        "id": 17,
                        "nodeType": "ExpressionStatement",
                        "src": "453:7:0",
                    }
                ],
            },
        }

        if_statement_node = self.cfg.add_node(
            node_id=f"{if_node['id']}-condition", node_type=if_node["nodeType"]
        )
        if_convergent_node = self.cfg.add_node(
            node_id=f"{if_node['id']}-convergent", node_type=if_node["nodeType"]
        )

        if_statement_expr = self.parse_expression(if_node["condition"])
        if_statement_node.add_statement(if_statement_expr)

        self.cfg.connect_nodes(
            parent_node,
            if_statement_node,
            annotation=f"Condition: {if_statement_expr}",
        )

        # Process the true body
        if "trueBody" in if_node:
            true_branch_node = self.cfg.add_node(
                node_id=f"{if_node['id']}-true", node_type=if_node["nodeType"]
            )
            self.cfg.connect_nodes(
                if_statement_node, true_branch_node, annotation=f"True"
            )
            self.parse_block(if_node["trueBody"], true_branch_node)
            self.cfg.connect_nodes(true_branch_node, if_convergent_node)
        # Process the false body
        if "falseBody" in if_node:
            false_branch_node = self.cfg.add_node(
                node_id=f"{if_node['id']}-false", node_type=if_node["nodeType"]
            )
            self.cfg.connect_nodes(
                if_statement_node, false_branch_node, annotation=f"False"
            )
            self.parse_block(if_node["falseBody"], false_branch_node)
            self.cfg.connect_nodes(
                false_branch_node,
                if_convergent_node,
            )

        return if_convergent_node

    def parse_return_statement(self, return_node, parent_node):
        """Parses a return statement and updates the control flow graph."""
        # Create a new CFG node for the return statement
        return_cfg_node = self.cfg.add_node(
            node_id=f"return_{return_node['id']}", node_type=return_node["nodeType"]
        )
        # If the return statement has an associated value, parse and add it
        if "expression" in return_node:
            expression = self.parse_expression(return_node["expression"])
            statement = ExpressionStatement(expression)
            return_cfg_node.add_statement(statement)
        # Connect the return node to the function exit node
        self.cfg.connect_nodes(parent_node, return_cfg_node)
        return return_cfg_node

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
            node_id=f"{for_node['id']}-init", node_type=for_node["nodeType"]
        )
        self.cfg.connect_nodes(parent_node, init_node)

        # Assuming you have a method to process the initialization part
        process_for_init(for_node["initializationExpression"], init_node)

        # Create a node for the loop condition
        loop_condition_node = self.cfg.add_node(
            node_id=f"{for_node['id']}-condition", node_type=for_node["nodeType"]
        )
        self.cfg.connect_nodes(init_node, loop_condition_node)

        # # Assuming you have a method to process the condition part
        process_for_condition(for_node["condition"], loop_condition_node)

        # Create a node for the body of the loop
        loop_body_node = self.cfg.add_node(
            node_id=f"{for_node['id']}_body", node_type=for_node["nodeType"]
        )
        self.cfg.connect_nodes(loop_condition_node, loop_body_node)

        # Parse the body of the loop
        self.parse_block(for_node["body"], loop_body_node)

        # Create a node for the increment/update part of the loop
        increment_node = self.cfg.add_node(
            node_id=f"{for_node['id']}_increment", node_type=for_node["nodeType"]
        )
        self.cfg.connect_nodes(loop_body_node, increment_node)

        # Assuming you have a method to process the increment part
        process_for_increment(for_node["loopExpression"], increment_node)

        # Create a back edge from the increment to the condition
        self.cfg.connect_nodes(increment_node, loop_condition_node)

        # Create a node for after the loop
        after_loop_node = self.cfg.add_node(
            node_id=f"{for_node['id']}_after", node_type=for_node["nodeType"]
        )
        self.cfg.connect_nodes(loop_condition_node, after_loop_node)

        return after_loop_node

    def parse_while_loop(self, while_node, parent_node):
        """
        Parses a while loop statement and updates the control flow graph.

        This method creates nodes for the loop condition and loop body, as well as for the
        continuation after the loop. It also connects these nodes to represent the flow of
        control, including the potential for loop repetition and exit."""
        # Create a node for the loop condition
        loop_condition_node = self.cfg.add_node(
            node_id=f"{while_node['id']}-condition",
            node_type=while_node["nodeType"],
        )
        self.cfg.connect_nodes(parent_node, loop_condition_node)
        condition_expression = self.parse_expression(while_node["condition"])
        loop_condition_node.add_statement(ExpressionStatement(condition_expression))

        # Create a node for the body of the loop
        loop_body_node = self.cfg.add_node(
            node_id=f"{while_node['id']}-body",
            node_type=while_node["nodeType"],
        )
        # Parse the body of the loop
        if "body" in while_node:
            print("parsing block for while node body")
            self.parse_block(while_node["body"], loop_body_node)

        # Create a back edge from the body to the condition (for repeating the loop)
        self.cfg.connect_nodes(loop_condition_node, loop_body_node)
        self.cfg.connect_nodes(loop_body_node, loop_condition_node)

        # Create a node for after the loop
        after_loop_node = self.cfg.add_node(
            node_id=f"{while_node['id']}-after",
            node_type=while_node["nodeType"],
        )
        self.cfg.connect_nodes(loop_condition_node, after_loop_node)

        return after_loop_node

    def parse_logical_expression(self, logical_expr_ast, parent_node):
        # Assuming logical_expr_ast is the AST node for "A || B" or "A && B"
        left_operand = logical_expr_ast["leftExpression"]
        right_operand = logical_expr_ast["rightExpression"]

        operator = logical_expr_ast["operator"]

        left_expr_str = self.parse_expression(left_operand)
        right_expr_str = self.parse_expression(right_operand)

        # Create nodes for evaluating left and right operands
        logical_expr_node = self.cfg.add_node(
            f"{left_operand['id']}-logical-expr", logical_expr_ast["nodeType"]
        )
        logical_expr_node.add_statement(f"{left_expr_str} {operator} {right_expr_str}")

        # Create CFG nodes for the left and right expressions
        left_node = self.cfg.add_node(
            f"{left_operand['id']}-logical-expr-left", logical_expr_ast["nodeType"]
        )
        left_node.add_statement(left_expr_str)

        right_node = self.cfg.add_node(
            f"{right_operand['id']}-logical-expr-right", logical_expr_ast["nodeType"]
        )
        right_node.add_statement(right_expr_str)

        # Connect the parent node to the left operand node
        self.cfg.connect_nodes(parent_node, left_node)

        # Create a bypass node for short-circuiting
        bypass_node = self.cfg.add_node(
            f"{logical_expr_ast['id']}-logical-expr-bypass",
            logical_expr_ast["nodeType"],
        )

        # Logic for short-circuiting
        self.cfg.connect_nodes(left_node, parent_node)
        self.cfg.connect_nodes(right_node, parent_node)
        if operator == "||":
            # For "||", if left is true, skip right operand
            self.cfg.connect_nodes(left_node, bypass_node, annotation="True")
            self.cfg.connect_nodes(left_node, right_node, annotation="False")
        elif operator == "&&":
            # For "&&", if left is false, skip right operand
            self.cfg.connect_nodes(left_node, bypass_node, annotation="False")
            self.cfg.connect_nodes(left_node, right_node, annotation="True")

        # Connect the right node to the bypass node
        self.cfg.connect_nodes(right_node, bypass_node)

        # The bypass node effectively acts as the convergent node
        return bypass_node
