from abc import ABC, abstractmethod


class AbstractAnalyzer(ABC):
    def __init__(self, ast_parser):
        self.ast_parser = ast_parser

    @abstractmethod
    def analyze(self):
        pass

    @abstractmethod
    def visualize(self):
        pass
