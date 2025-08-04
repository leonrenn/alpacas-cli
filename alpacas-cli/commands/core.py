"Core command and analysis classes for the management system."

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from dataclasses import dataclass


@dataclass
class CommandResult:
    success: bool
    message: Optional[str] = None
    data: Any = None
    should_exit: bool = False  # New field specifically for exit status


class Command(ABC):
    """
    Abstract base class for commands in the management system.

    Commands should implement the `execute` method to perform their actions.
    """

    @abstractmethod
    def execute(self, context) -> CommandResult:
        """
        Execute the command with the given context.
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """
        Return a brief description of the command.
        """
        pass


@dataclass
class ExchangeStatus:
    is_open: bool
    name: str
    current_time: str
    status_message: str


@dataclass
class AnalysisResult:
    """Container for analysis results."""

    title: str
    data: Dict[str, Any]
    summary: str


class Analysis(ABC):
    @abstractmethod
    def run(self) -> AnalysisResult:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("Analysis", "")


class StoppableAnalysis(Analysis, ABC):
    def __init__(self):
        self._stop_requested = False

    def stop(self):
        self._stop_requested = True

    def should_stop(self) -> bool:
        return self._stop_requested
