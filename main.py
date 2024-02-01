from src.parsers.ast_parser import ASTParser
from src.analyzers.class_hierarchy_analyzer import ClassHierarchyAnalyzer
from src.analyzers.call_graph_analyzer import CallGraphAnalyzer
from src.analyzers.control_flow_graph_analyzer import ControlFlowGraphAnalyzer
from src.analyzers.data_flow_analyzer import DataFlowAnalyzer

if __name__ == "__main__":
    # ast_file_path = "output/example.sol_json.ast"
    file_path = "contracts/HelloWorld.sol"
    parser = ASTParser(file_path)
    parser.parse()

    # Class Hierarchy Analysis
    class_hierarchy_analyzer = ClassHierarchyAnalyzer(parser)
    class_hierarchy_analyzer.analyze()

    # Call Graph Analysis
    call_graph_analyzer = CallGraphAnalyzer(parser, class_hierarchy_analyzer)
    call_graph_analyzer.analyze("RTA")
    call_graph_analyzer.analyze("CHA")

    # Control Flow Analysis
    control_flow_graph_analyzer = ControlFlowGraphAnalyzer(parser)
    control_flow_graph_analyzer.analyze()

    # Data Flow Analysis
    # data_flow_analyzer = DataFlowAnalyzer(parser, control_flow_graph_analyzer)
    # data_flow_analyzer.analyze()
