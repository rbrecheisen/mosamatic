from abc import ABC, abstractmethod


class BaseUI(ABC):
    @abstractmethod
    def start(self):
        pass