import json
import subprocess
import os
from src.parsers.nodes import ASTNode


class SolidityASTParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.source_code = None
        self.ast = None

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

        for file in os.listdir("output"):
            if file.endswith(".ast"):
                with open(f"output/{file}", "r") as ast_file:
                    self.ast = json.load(ast_file)
                    break

        ast = ASTNode.create(self.ast)
        representation = ast.visualize()
        print("respresentation ", representation)
