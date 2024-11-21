import coverage
from contextlib import contextmanager
import time
import psutil
import logging
from pathlib import Path

class ProfilingManager:
    def __init__(self):
        config_file = str(Path(__file__).parent.parent / ".coveragerc")
        self.cov = coverage.Coverage(config_file=config_file)
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def profile_request(self, request_id: str):
        start_time = time.time()
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            self.cov.start()
            yield
        finally:
            self.cov.stop()
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024
            
            metrics = {
                'request_id': request_id,
                'execution_time': end_time - start_time,
                'memory_used': end_memory - start_memory,
                'total_memory': end_memory
            }
            
            self.logger.info(f"Request profiling metrics: {metrics}")
            
    def generate_coverage_report(self):
        self.cov.save()
        return self.cov.report()

    def profile_database(self, query):
        start_time = time.time()
        try:
            return query()
        finally:
            execution_time = time.time() - start_time
            self.logger.info(f"Database query execution time: {execution_time:.4f}s")