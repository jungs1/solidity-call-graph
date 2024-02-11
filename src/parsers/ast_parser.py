import json
import subprocess
import os
from src.parsers.nodes import ASTNode


class SolidityASTParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.source_code = None
        self.ast = None
        self.ast_v2 = None

    def load_code_file_file(self, file_path: str) -> None:
        """Load the source code from a file."""
        with open(file_path, "r") as code_file:
            source_code = code_file.read()
        return source_code

    def parse(self) -> None:
        """Parse Solidity source code to generate the AST.
        This method would require integration with a Solidity compiler or parser.
        """
        self.source_code = self.load_code_file_file(self.file_path)

        subprocess.run(
            [
                "solc",
                "-o",
                "output",
                "--bin",
                "--ast-compact-json",
                "--asm",
                "--overwrite",
                self.file_path,
            ],
            check=True,
        )
        print("file_path", self.file_path)  # contracts/example.sol
        filename = self.file_path.split("/")[-1].split(".")[0]

        for file in os.listdir("output"):
            with open(f"output/{filename}.sol_json.ast", "r") as ast_file:
                self.ast = json.load(ast_file)
                break

        self.ast_v2 = ASTNode.create(self.ast)
        {
            "arguments": [],
            "expression": {
                "argumentTypes": [],
                "id": 44,
                "isConstant": False,
                "isLValue": False,
                "isPure": False,
                "lValueRequested": False,
                "nodeType": "NewExpression",
                "src": "578:11:0",
                "typeDescriptions": {
                    "typeIdentifier": "t_function_creation_nonpayable$__$returns$_t_contract$_Bitcoin_$21_$",
                    "typeString": "function () returns (contract Bitcoin)",
                },
                "typeName": {
                    "id": 43,
                    "nodeType": "UserDefinedTypeName",
                    "pathNode": {
                        "id": 42,
                        "name": "Bitcoin",
                        "nameLocations": ["582:7:0"],
                        "nodeType": "IdentifierPath",
                        "referencedDeclaration": 21,
                        "src": "582:7:0",
                    },
                    "referencedDeclaration": 21,
                    "src": "582:7:0",
                    "typeDescriptions": {
                        "typeIdentifier": "t_contract$_Bitcoin_$21",
                        "typeString": "contract Bitcoin",
                    },
                },
            },
            "id": 45,
            "isConstant": False,
            "isLValue": False,
            "isPure": False,
            "kind": "functionCall",
            "lValueRequested": False,
            "nameLocations": [],
            "names": [],
            "nodeType": "FunctionCall",
            "src": "578:13:0",
            "tryCall": False,
            "typeDescriptions": {
                "typeIdentifier": "t_contract$_Bitcoin_$21",
                "typeString": "contract Bitcoin",
            },
        }
        representation = self.ast_v2.visualize()
        print(representation)
