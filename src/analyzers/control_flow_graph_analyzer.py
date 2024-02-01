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


class DeclarationStatement(Statement):
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

    def add_statement(self, statement):
        """Add a statement to the node's list of statements."""
        self.statements.append(statement)

    def add_incoming_edge(self, node, annotation=None):
        """Add an incoming edge to the node."""
        self.incoming_edges.append((node, annotation))

    def add_outgoing_edge(self, node, annotation=None):
        """Add an outgoing edge to the node."""
        self.outgoing_edges.append((node, annotation))

    def format_label(self):
        """Create a human-readable label for the node."""
        label_parts = [f"Node: {self.node_id} ({self.node_type})"]
        print("labl_parts", label_parts)
        for statement in self.statements:
            label_parts.append(f"  {statement}")
        # label_parts.extend(self.statements)
        return "\n".join(label_parts)


class ControlFlowGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, CFGNode] = {}
        self.function_nodes: Dict[str, Tuple[CFGNode, CFGNode]] = {}

    def connect_function_call(
        self, caller_node: CFGNode, function_id: str
    ) -> Optional[CFGNode]:
        """Connect the caller node to the entry of the called function."""
        entry_node, exit_node = self.function_nodes.get(function_id, (None, None))
        if entry_node:
            self.connect_nodes(caller_node, entry_node)
            # Assuming the caller node will receive control back after the function call
            return_node = self.add_node(f"return_from_{function_id}")
            self.connect_nodes(exit_node, return_node)
            return return_node
        return None

    def add_node(self, node_id: str, node_type: str) -> CFGNode:
        """Add a new node to the control flow graph."""
        if type(node_id) == int:
            node_id = str(node_id)
        return self._create_and_add_node(node_id, node_type)

    def find_node(self, node_id: str) -> Optional[CFGNode]:
        """Find a node in the control flow graph by its ID."""
        return self.nodes.get(node_id, None)

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

    def _create_and_add_node(self, node_id: str, node_type: str) -> CFGNode:
        node = CFGNode(node_id=node_id, node_type=node_type)
        self.nodes[node_id] = node
        return node

    def pretty_print_nodes(self) -> None:
        """Print a human-readable representation of the nodes in the graph."""
        for node_id, node in self.nodes.items():
            print(node.format_label())
            print(
                f"Incoming edges: {[(n.node_id, ann) for n, ann in node.incoming_edges]}"
            )
            print(
                f"Outgoing edges: {[(n.node_id, ann) for n, ann in node.outgoing_edges]}"
            )
            print("--------------------------")


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
            "IfStatement Convergent": "orange",
            "WhileStatement": "orange",
            "ForInit": "orange",
            "ForCondition": "orange",
            "ForBody": "orange",
            "AfterFor": "orange",
            "ForIncrement": "orange",
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

    def get_source_snippet(self, src):
        start, length = map(int, src.split(":")[:2])

        return self.parser.source_code[start : start + length]

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
        statement = DeclarationStatement(variable_name, variable_type, initial_value)
        parent_node.add_statement(statement)
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
