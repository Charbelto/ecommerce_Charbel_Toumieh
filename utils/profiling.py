from functools import wraps
import cProfile
import pstats
import io
import time
from memory_profiler import profile as memory_profile
import coverage

def performance_profile(output_file=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            try:
                return profiler.runcall(func, *args, **kwargs)
            finally:
                if output_file:
                    profiler.dump_stats(output_file)
                else:
                    # Print profiling stats
                    s = io.StringIO()
                    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
                    stats.print_stats()
                    print(s.getvalue())
        return wrapper
    return decorator

def track_memory_usage(func):
    @wraps(func)
    @memory_profile
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper