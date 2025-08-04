"""
Core module for running analyses asynchronously.
"""

import threading
import uuid
from commands.core import StoppableAnalysis


class AsyncAnalysisRunner:
    def __init__(self, analysis: StoppableAnalysis):
        self.analysis = analysis
        self.thread = threading.Thread(target=self._run)
        self.result = None
        self.exception = None
        self.id = str(uuid.uuid4())

    def _run(self):
        try:
            self.result = self.analysis.run()
        except Exception as e:
            self.exception = e

    def start(self):
        self.thread.start()

    def stop(self):
        self.analysis.stop()

    def is_running(self):
        return self.thread.is_alive()

    def get_result(self):
        if self.thread.is_alive():
            return None
        if self.exception:
            raise self.exception
        return self.result
