from abc import ABCMeta, abstractmethod


class BaseInstructionsTranslator(metaclass=ABCMeta):
    def __init__(self, instruction: str):
        self._instruction = instruction.lower()

    @abstractmethod
    def translated(self) -> str:
        ...
