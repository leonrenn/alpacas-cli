"""
Defintion of analyses.
"""

from analysis.core import StoppableAnalysis
from commands.core import AnalysisResult
import time


class SampleAnalysis(StoppableAnalysis):
    def run(self) -> AnalysisResult:

        for i in range(100):
            if self.should_stop():
                return AnalysisResult(
                    title="Sample Analysis", data={}, summary="Stopped early."
                )
            time.sleep(1)
        return AnalysisResult(
            title="Sample Analysis", data={}, summary="Completed successfully."
        )

    def get_description(self) -> str:
        return "A test analysis that runs for 100 seconds."
