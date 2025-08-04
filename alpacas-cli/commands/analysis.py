"""
Commands with respect to running analyses available via the command manager.
"""

from typing import List
from .core import (
    Command,
    CommandResult,
    StoppableAnalysis,
    Analysis,
)
from analysis.analysis import SampleAnalysis
from analysis.core import AsyncAnalysisRunner
from typing import Dict, Union
from utils.pretty_printing import (
    pretty_print_available_analyses,
    pretty_print_running_analyses,
)
from utils.input_validation import (
    is_valid_analysis_subcommand,
    is_non_empty_string,
    get_validated_input,
)


class AnalysisCommand(Command):
    """Command to manage and run portfolio analyses."""

    def __init__(self, context):
        self.analyses: Dict[str, Union[StoppableAnalysis, Analysis]] = (
            self._init_analyses(context=context)
        )
        self.running_analyses: Dict[str, AsyncAnalysisRunner] = {}

    def _init_analyses(self, context) -> Dict[str, Union[StoppableAnalysis, Analysis]]:
        """Initialize available analyses."""
        # All analyses need to be registered here to be available for execution.
        # NOTE: Context included to allow analyses that interact with the portfolio.
        return {"sample_analysis": SampleAnalysis()}

    def execute(self, context) -> CommandResult:  # type: ignore
        if not context.loaded_portfolio_name:
            return CommandResult(
                success=False,
                message="No portfolio loaded. Please load or create a portfolio first.",
            )

        self._show_available_analyses()
        valid_analysis_subcommands: List[str] = [
            "status",
            "stop",
        ] + list(self.analyses.keys())
        choice = get_validated_input(
            "\nEnter analysis name ('status', 'stop <id>'): ",
            [is_non_empty_string, is_valid_analysis_subcommand],  # type: ignore
            valid_analysis_subcommands,
        )

        if choice == "status":
            return self._show_status()
        elif choice.startswith("stop "):
            analysis_id: str = str(choice.split(" ", 1))
            return self._stop_analysis(analysis_id)
        elif choice in self.analyses:
            # Check if the analysis is stoppable
            if isinstance(self.analyses[choice], StoppableAnalysis):
                stoppable = True
                return self._start_analysis(choice, context, stoppable=stoppable)
            elif isinstance(self.analyses[choice], Analysis):
                # Non-stoppable analysis
                try:
                    result: CommandResult = self._start_analysis(
                        choice, context, stoppable=False
                    )
                except KeyboardInterrupt:
                    return CommandResult(success=False, message="Analysis interrupted.")
                return result
        else:
            return CommandResult(success=False, message="Unknown analysis.")

    def _start_analysis(
        self, name: str, context, stoppable: bool = True
    ) -> CommandResult:
        if stoppable:
            runner = AsyncAnalysisRunner(self.analyses[name])  # type: ignore
            runner.start()
            self.running_analyses[runner.id] = runner
            context.analysis_runners.append(runner)
            return CommandResult(
                success=True, message=f"{name} started with ID {runner.id}"
            )
        else:
            try:
                result = self.analyses[name].run()
                return CommandResult(
                    success=True,
                    message=f"{name} completed successfully.",
                    data=result.data,
                )
            except Exception as e:
                return CommandResult(
                    success=False, message=f"Error running {name}: {str(e)}"
                )

    def _stop_analysis(self, analysis_id: str) -> CommandResult:
        runner = self.running_analyses.get(analysis_id)
        if not runner or not runner.is_running():
            return CommandResult(
                success=False, message=f"No running analysis with ID '{analysis_id}'."
            )
        runner.stop()
        return CommandResult(
            success=True,
            message=f"Stop signal sent to analysis with ID '{analysis_id}'.",
        )

    def _show_status(self) -> CommandResult:
        pretty_print_running_analyses(running_analyses=self.running_analyses)
        return CommandResult(success=True)

    def _show_available_analyses(self) -> None:
        pretty_print_available_analyses(analyses=self.analyses)

    def description(self) -> str:
        return "Run various analyses on the portfolio"
