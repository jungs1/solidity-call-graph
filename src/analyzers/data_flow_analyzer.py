from src.analyzers.abstract_analyzer import AbstractAnalyzer
from src.analyzers.control_flow_graph_analyzer import ControlFlowGraphAnalyzer


class DataFlowAnalyzer(AbstractAnalyzer):
    def __init__(self, parser, cfg_analyzer: ControlFlowGraphAnalyzer):
        self.parser = parser
        self.cfg_analyzer = cfg_analyzer
        # Reaching Definitions
        self.in_sets = {}
        self.out_sets = {}
        # Live Variables
        self.live_in_sets = {}
        self.live_out_sets = {}

        for node_id in cfg_analyzer.cfg.nodes:
            self.in_sets[node_id] = set()
            self.out_sets[node_id] = set()
            self.live_in_sets[node_id] = set()
            self.live_out_sets[node_id] = set()
        print("DataFlowAnalyzer initialized")

    def visualize(self):
        pass

    def analyze(self):
        """Perform data flow analysis on the control flow graph."""
        print("DataFlowAnalyzer analyzed")
        self.compute_reaching_definitions()
        print("-----")
        self.compute_live_variables()

    def compute_live_variables(self):
        changed = True
        while changed:
            changed = False
            # Process nodes in reverse order since it's a backward analysis
            for node_id in reversed(list(self.cfg_analyzer.cfg.nodes.keys())):
                node = self.cfg_analyzer.cfg.nodes[node_id]

                # Calculate Live-Out by union of Live-In of all successors
                live_out = set()
                for succ_node, _ in node.outgoing_edges:
                    live_out |= self.live_in_sets[succ_node.node_id]

                if live_out != self.live_out_sets[node_id]:
                    self.live_out_sets[node_id] = live_out
                    changed = True

                # Directly use uses and defs from CFGNode
                uses = node.uses  # Directly access the uses set from the node
                defs = node.defs  # Directly access the defs set from the node
                live_in = uses | (live_out - defs)

                if live_in != self.live_in_sets[node_id]:
                    self.live_in_sets[node_id] = live_in
                    changed = True

                # Optional: print all relevant sets for debugging/verification
                print("Node:", node_id)
                print("Live-IN:", live_in)
                print("Live-OUT:", live_out)
                print("\n")

    def get_uses(self, node):
        # Placeholder for extracting variables used in the node before any assignment
        uses = set()
        # Implement logic to populate `uses` based on the node's statements
        return uses

    def get_defs(self, node):
        # Placeholder for extracting variables defined (assigned) in the node
        defs = set()
        # Implement logic to populate `defs` based on the node's statements
        return defs

    def compute_reaching_definitions(self):
        """Compute reaching definitions for each node in the CFG."""
        changed = True
        while changed:
            changed = False
            for node_id, node in self.cfg_analyzer.cfg.nodes.items():
                # Calculate IN[node] as the union of OUT[p] for all predecessors p of node
                in_set = set()
                for pred_node, _ in node.incoming_edges:
                    in_set |= self.get_out_set(pred_node.node_id)

                if in_set != self.get_in_set(node_id):
                    self.in_sets[node_id] = in_set
                    changed = True

                # Directly use the gen set as computed in the CFGNode
                gen_set = {var for _, var, _ in node.gens}

                # Calculate KILL[node] - Definitions in IN that are redefined by this node
                # This requires identifying variables defined in this node that could potentially
                # kill definitions reaching this node from its predecessors.
                kill_set = {
                    def_var
                    for def_var in self.calculate_all_defs()
                    if def_var in gen_set and def_var in in_set
                }

                # OUT[node] = GEN[node] U (IN[node] - KILL[node])
                # Here, we adjust to consider the gen set's variables for the union operation.
                out_set = gen_set | (in_set - kill_set)

                if out_set != self.get_out_set(node_id):
                    self.out_sets[node_id] = out_set
                    changed = True

                # print all relveant sets
                print("Node:", node_id)
                print("IN:", in_set)
                print("GEN:", gen_set)
                print("KILL:", kill_set)
                print("OUT:", out_set)
                print("\n")

    def get_out_set(self, node_id):
        """Get the OUT set for a node, identified by its node_id."""
        return self.out_sets.get(node_id, set())

    def get_in_set(self, node_id):
        """Get the IN set for a node, identified by its node_id."""
        return self.in_sets.get(node_id, set())

    def calculate_all_defs(self):
        """Aggregate all definitions across the CFG to assist in calculating KILL sets."""
        all_defs = set()
        for node in self.cfg_analyzer.cfg.nodes.values():
            all_defs |= (
                node.defs
            )  # Assuming node.defs is a set of variable names defined by the node
        return all_defs
