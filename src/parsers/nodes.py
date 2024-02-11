class ASTNode:
    def __init__(self, node):
        self.id = node.get("id")
        self.nodeType = node.get("nodeType")
        self.src = node.get("src")

    @staticmethod
    def create(node):
        nodeType = node.get("nodeType")
        if nodeType == "SourceUnit":
            return SourceUnit(node)
        elif nodeType == "ContractDefinition":
            return ContractDefinition(node)
        elif nodeType == "Block":
            return Block(node)
        elif nodeType == "VariableDeclaration":
            return VariableDeclaration(node)
        elif nodeType == "VariableDeclarationStatement":
            return VariableDeclarationStatement(node)
        elif nodeType == "ExpressionStatement":
            return ExpressionStatement(node)
        elif nodeType == "IfStatement":
            return IfStatement(node)
        elif nodeType == "BinaryOperation":
            return BinaryOperation(node)
        elif nodeType == "FunctionDefinition":
            return FunctionDefinition(node)
        elif nodeType == "PragmaDirective":
            return PragmaDirective(node)
        elif nodeType == "ElementaryTypeName":
            return ElementaryTypeName(node)
        elif nodeType == "Literal":
            return Literal(node)
        elif nodeType == "Assignment":
            return Assignment(node)
        elif nodeType == "Return":
            return Return(node)
        elif nodeType == "Identifier":
            return Identifier(node)
        elif nodeType == "WhileStatement":
            return WhileStatement(node)
        elif nodeType == "UnaryOperation":
            return UnaryOperation(node)

        else:
            print("", node)
            raise Exception(f"Unknown node type: {nodeType}")

    def visualize(self, level=0):
        indent = "  " * level
        representation = f"{indent}{self.nodeType} (ID: {self.id})\n"
        # representation += f"{indent}  Src: {self.src}\n"
        return representation


class SourceUnit(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.license = node.get("license")
        self.nodes = [ASTNode.create(n) for n in node.get("nodes", [])]

    def visualize(self, level=0):
        representation = super().visualize(level)
        for node in self.nodes:
            node_repr = node.visualize(level + 1)
            if node_repr:
                representation += node_repr
        return representation


class ContractDefinition(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.name = node.get("name")
        self.baseContracts = node.get("baseContracts")
        self.nodes = [ASTNode.create(n) for n in node.get("nodes", [])]

    def visualize(self, level=0):
        representation = super().visualize(level)
        for node in self.nodes:
            node_repr = node.visualize(level + 1)
            if node_repr:
                representation += node_repr
        return representation


class WhileStatement(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.condition = ASTNode.create(node.get("condition"))
        self.body = ASTNode.create(node.get("body"))
        self.nodes = [ASTNode.create(n) for n in node.get("nodes", [])]

    def visualize(self, level=0):
        representation = super().visualize(level)
        if self.condition:
            representation += self.condition.visualize(level + 1)
        if self.body:
            representation += self.body.visualize(level + 1)
        return representation


class UnaryOperation(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.operator = node.get("operator")  # (e.g) ++, --
        self.subExpression = ASTNode.create(node.get("subExpression"))

    def visualize(self, level=0):
        representation = super().visualize(level)
        if self.subExpression:
            representation += self.subExpression.visualize(level + 1)
        return representation


class Return(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.expression = (
            ASTNode.create(node.get("expression")) if node.get("expression") else None
        )
        self.functionReturnParameters = node.get("functionReturnParameters")

    def visualize(self, level=0):
        indent = "  " * level
        representation = f"{indent}{self.nodeType}:\n"
        if self.expression:
            representation += (
                f"{indent}  Expression:\n {self.expression.visualize(level + 1)}"
            )
        else:
            representation += f"{indent}  No return expression\n"
        return representation


class IfStatement(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.condition = ASTNode.create(node.get("condition"))
        self.trueBody = (
            ASTNode.create(node.get("trueBody")) if node.get("trueBody") else None
        )
        self.falseBody = (
            ASTNode.create(node.get("falseBody")) if node.get("falseBody") else None
        )

    def visualize(self, level=0):
        indent = "  " * level
        representation = f"{indent}{self.nodeType}:\n"
        representation += f"{indent}  Condition:\n{self.condition.visualize(level + 2)}"
        if self.trueBody:
            representation += (
                f"{indent}  True Body:\n{self.trueBody.visualize(level + 2)}"
            )
        if self.falseBody:
            representation += (
                f"{indent}  False Body:\n{self.falseBody.visualize(level + 2)}"
            )
        return representation


class BinaryOperation(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.operator = node.get("operator")
        self.leftExpression = ASTNode.create(node.get("leftExpression"))
        self.rightExpression = ASTNode.create(node.get("rightExpression"))

    def visualize(self, level=0):
        indent = "  " * level
        representation = f"{indent}{self.nodeType} (Operator: {self.operator}):\n"
        representation += (
            f"{indent}  Left Expression:\n{self.leftExpression.visualize(level + 2)}"
        )
        representation += (
            f"{indent}  Right Expression:\n{self.rightExpression.visualize(level + 2)}"
        )
        return representation


class VariableDeclaration(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.name = node.get("name")
        self.typeString = node.get("typeDescriptions", {}).get("typeString")
        self.visibility = node.get("visibility")
        self.value = node.get("value", {}).get("value")

    def visualize(self, level=0):
        representation = super().visualize(level)
        return representation


class Assignment(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.operator = node.get("operator")  # The assignment operator, e.g., "="
        # Assuming the left-hand side (lhs) is provided similarly to the right-hand side (rhs) in the AST
        self.leftHandSide = ASTNode.create(
            node.get("leftHandSide")
        )  # Create the lhs node
        self.rightHandSide = ASTNode.create(
            node.get("rightHandSide")
        )  # Create the rhs node, which is detailed in the example

    def visualize(self, level=0):
        indent = "  " * level
        representation = f"{indent}{self.nodeType} (Operator: {self.operator}):\n"
        representation += (
            f"{indent}  Left Hand Side:\n{self.leftHandSide.visualize(level + 2)}"
        )
        representation += (
            f"{indent}  Right Hand Side:\n{self.rightHandSide.visualize(level + 2)}"
        )
        return representation


class VariableDeclarationStatement(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.declarations = [
            VariableDeclaration(decl) for decl in node.get("declarations")
        ]

    def visualize(self, level=0):
        representation = super().visualize(level)
        for decl in self.declarations:
            decl_repr = decl.visualize(level + 1)
            if decl_repr:
                representation += decl_repr
        return representation


class PragmaDirective(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.literals = node.get("literals", [])  # e.g., ["solidity", "^", "0.8", ".0"]

    def visualize(self, level=0):
        indent = "  " * level
        literals_str = " ".join(self.literals)
        return f"{indent}{self.nodeType}: {literals_str}\n"


class ElementaryTypeName(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.name = node.get("name")  # e.g., "uint256", "address"

    def visualize(self, level=0):
        indent = "  " * level
        return f"{indent}{self.nodeType}: {self.name}\n"


class FunctionDefinition(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.name = node.get("name")
        self.visibility = node.get("visibility")
        self.stateMutability = node.get("stateMutability")
        self.parameters = [
            ASTNode.create(n) for n in node.get("parameters", {}).get("parameters", [])
        ]
        self.returnParameters = [
            ASTNode.create(n)
            for n in node.get("returnParameters", {}).get("parameters", [])
        ]
        self.body = ASTNode.create(node.get("body")) if node.get("body") else None

    def visualize(self, level=0):
        representation = super().visualize(level)
        if self.body:
            representation += self.body.visualize(level + 1)
        return representation


class Block(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.statements = [ASTNode.create(stmt) for stmt in node.get("statements", [])]

    def visualize(self, level=0):
        indent = "  " * level
        representation = f"{indent}{self.nodeType}:\n"
        for stmt in self.statements:
            representation += stmt.visualize(level + 1)
        return representation


class ExpressionStatement(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.expression = ASTNode.create(node.get("expression"))

    def visualize(self, level=0):
        indent = "  " * level
        return f"{indent}{self.nodeType}:\n {self.expression.visualize(level + 1)}"


class Literal(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.kind = node.get("kind")  # e.g., "string", "number"
        self.value = node.get("value")  # The literal value, e.g., "Hello World", "100"

    def visualize(self, level=0):
        indent = "  " * level
        return f"{indent}{self.nodeType} ({self.kind}): {self.value}\n"


class Identifier(ASTNode):
    def __init__(self, node):
        super().__init__(node)
        self.name = node.get("name")  # e.g., "uint256", "address"

    def visualize(self, level=0):
        indent = "  " * level
        return f"{indent}{self.nodeType}: {self.name}\n"
