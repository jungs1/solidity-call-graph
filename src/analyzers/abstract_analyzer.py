from abc import ABC, abstractmethod


class AbstractAnalyzer(ABC):
    def __init__(self, parser):
        self.parser = parser

    @abstractmethod
    def analyze(self):
        pass

    @abstractmethod
    def visualize(self):
        pass
