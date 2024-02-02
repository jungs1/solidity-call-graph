from src.analyzers.abstract_analyzer import AbstractAnalyzer


class DataFlowGraph:
    def __init__(self, control_flow_graph):
        self.cfg = control_flow_graph
        self.dfg = self.build_data_flow_graph()

    def build_data_flow_graph(self):
        # Initialize the data flow graph based on the control flow graph
        dfg = {}
        for node in self.cfg.nodes:
            # For each node in the CFG, create corresponding nodes and edges in the DFG
            # based on variable definitions and uses
            pass
        return dfg


class DataFlowAnalyzer(AbstractAnalyzer):
    def __init__(self, cfg):
        self.cfg = cfg
        self.in_sets = {node_id: set() for node_id in cfg.nodes}
        self.out_sets = {node_id: set() for node_id in cfg.nodes}

    def compute_reaching_definitions(self):
        """Compute reaching definitions for each node in the CFG."""
        changed = True
        while changed:
            changed = False
            for node_id, node in self.cfg.nodes.items():
                in_old = self.in_sets[node_id]
                # Compute IN by union of OUT sets of all predecessors
                self.in_sets[node_id] = (
                    set.union(*(self.out_sets[p.node_id] for p in node.predecessors))
                    if node.predecessors
                    else set()
                )

                # Compute OUT as IN plus current node's definitions
                out_new = self.in_sets[node_id].union(node.definitions)

                if out_new != self.out_sets[node_id]:
                    self.out_sets[node_id] = out_new
                    changed = True

    def get_in_set(self, node_id):
        """Get the IN set for a node."""
        return self.in_sets.get(node_id, set())

    def get_out_set(self, node_id):
        """Get the OUT set for a node."""
        return self.out_sets.get(node_id, set())
