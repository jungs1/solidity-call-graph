from src.parsers.ast_parser import ASTParser
from src.analyzers.class_hierarchy_analyzer import ClassHierarchyAnalyzer
from src.analyzers.call_graph_analyzer import CallGraphAnalyzer
from src.analyzers.control_flow_graph_analyzer import ControlFlowGraphAnalyzer

if __name__ == "__main__":
    # ast_file_path = "output/example.sol_json.ast"
    file_path = "contracts/HelloWorld.sol"
    parser = ASTParser(file_path)
    parser.parse()

    # CHA
    class_hierarchy_analyzer = ClassHierarchyAnalyzer(parser)
    class_hierarchy_analyzer.analyze()

    # Call Graph
    call_graph_analyzer = CallGraphAnalyzer(parser)
    call_graph_analyzer.analyze("RTA")
    call_graph_analyzer.analyze("CHA")

    # Control Flow Graph
    control_flow_graph_analyzer = ControlFlowGraphAnalyzer(parser)
    control_flow_graph_analyzer.analyze()
