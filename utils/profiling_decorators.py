from functools import wraps
import cProfile
import pstats
import io
import time

def detailed_profile(output_prefix=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            start_time = time.time()
            
            try:
                result = profiler.runcall(func, *args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                
                if output_prefix:
                    # Save profiling stats to file
                    stats = pstats.Stats(profiler)
                    stats.sort_stats('cumulative')
                    output_file = f"{output_prefix}_{int(time.time())}.prof"
                    stats.dump_stats(output_file)
                    
                    # Print basic stats
                    s = io.StringIO()
                    stats.stream = s
                    stats.print_stats()
                    print(f"Function: {func.__name__}")
                    print(f"Duration: {duration:.2f} seconds")
                    print(s.getvalue())
        
        return wrapper
    return decorator
