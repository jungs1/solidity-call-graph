class CFGNode:
    """Represents a node in the Control Flow Graph."""

    def __init__(self, node_id, node_type):
        self.node_id = node_id
        self.node_type = node_type
        self.statements = []
        self.incoming_edges = []  # List of tuples (node, annotation)
        self.outgoing_edges = []  # List of tuples (node, annotation)

    def add_statement(self, statement):
        self.statements.append(statement)

    def add_incoming_edge(self, node, annotation=None):
        self.incoming_edges.append((node, annotation))

    def add_outgoing_edge(self, node, annotation=None):
        self.outgoing_edges.append((node, annotation))

    def format_label(self):
        # Create a human-readable label for the node
        label_parts = [f"Node: {self.node_id} ({self.node_type})"]
        label_parts.extend(self.statements)
        return "\n".join(label_parts)


class ControlFlowGraph:
    def __init__(self):
        self.nodes = {}
        self.function_nodes = {}

    def connect_function_call(self, caller_node, function_id):
        # Connect the caller node to the entry of the called function
        entry_node, exit_node = self.function_nodes.get(function_id, (None, None))
        if entry_node:
            self.connect_nodes(caller_node, entry_node)
            # Assuming the caller node will receive control back after the function call
            return_node = self.add_node(f"return_from_{function_id}")
            self.connect_nodes(exit_node, return_node)
            return return_node
        return None

    def add_node(self, node_id, node_type):
        if type(node_id) == int:
            node_id = str(node_id)
        node = CFGNode(node_id=node_id, node_type=node_type)
        self.nodes[node_id] = node
        return node

    def find_node(self, node_id):
        return self.nodes.get(node_id, None)

    def add_function_entry_exit(self, function_id, function_name):
        # Create entry and exit nodes for a function
        entry_node = self.add_node(
            f"entry_{function_id}_{function_name}", "FunctionEntry"
        )
        exit_node = self.add_node(f"exit_{function_id}_{function_name}", "FunctionExit")
        self.function_nodes[f"{function_id}_{function_name}"] = (entry_node, exit_node)
        return entry_node, exit_node

    def connect_nodes(self, from_node, to_node, annotation=None):
        from_node.add_outgoing_edge(to_node, annotation)
        to_node.add_incoming_edge(from_node, annotation)

    def pretty_print_nodes(self):
        for node_id, node in self.nodes.items():
            print(f"Node: {node_id} {node}")
            print(f"Statements: {node.statements}")
            print(f"Incoming edges: {node.incoming_edges}")
            print(f"Outgoing edges: {node.outgoing_edges}")
            print("--------------------------")
