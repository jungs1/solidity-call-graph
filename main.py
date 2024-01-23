import json
from ast_parser import ASTParser

if __name__ == "__main__":
    with open("output/example.sol_json.ast") as f:
        data = json.load(f)

    with open("contracts/example.sol", "r") as file:
        source_code = file.read()
    parser = ASTParser(data, source_code)
    # parser.control_flow_graph_analyzer.analyze()
    parser.class_hierarchy_analyzer.analyze()
    parser.call_graph_analyzer.analyze()
