from functools import wraps
import cProfile
import pstats
import io
import time
import tracemalloc
from datetime import datetime
from pathlib import Path
from .profiling_config import (
    PROFILE_OUTPUT_DIR, 
    PERFORMANCE_SETTINGS,
    MEMORY_SETTINGS
)

def detailed_profile(output_prefix=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create output directory if it doesn't exist
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = PROFILE_OUTPUT_DIR / f"{output_prefix}_{timestamp}" if output_prefix else PROFILE_OUTPUT_DIR / timestamp
            output_dir.mkdir(parents=True, exist_ok=True)

            # Start memory tracking
            tracemalloc.start()
            start_memory = tracemalloc.get_traced_memory()

            # Start performance profiling
            profiler = cProfile.Profile()
            start_time = time.time()

            try:
                # Run the function with profiling
                result = profiler.runcall(func, *args, **kwargs)
                return result
            finally:
                # Collect memory stats
                current_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                # Save performance profile
                perf_stats = pstats.Stats(profiler)
                perf_stats.sort_stats('cumulative')
                perf_stats.dump_stats(output_dir / 'performance.prof')

                # Generate report
                report = {
                    'function': func.__name__,
                    'execution_time': time.time() - start_time,
                    'memory': {
                        'peak': current_memory[1] / 1024 / 1024,  # MB
                        'increase': (current_memory[0] - start_memory[0]) / 1024 / 1024  # MB
                    },
                    'timestamp': timestamp
                }

                # Save report
                with open(output_dir / 'report.txt', 'w') as f:
                    f.write(f"Function: {report['function']}\n")
                    f.write(f"Execution Time: {report['execution_time']:.2f} seconds\n")
                    f.write(f"Peak Memory: {report['memory']['peak']:.2f} MB\n")
                    f.write(f"Memory Increase: {report['memory']['increase']:.2f} MB\n")
                    f.write(f"Timestamp: {report['timestamp']}\n")
