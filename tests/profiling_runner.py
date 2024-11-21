import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.profiling import performance_profile, track_memory_usage
import pytest
import cProfile
import pstats

def run_profiled_tests():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run pytest programmatically
    pytest.main(['tests/', '-v', '--cov=services', '--cov-report=html'])
    
    profiler.disable()
    
    # Save profiling results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.dump_stats('test_profiling_results.prof')
    stats.print_stats()

if __name__ == '__main__':
    run_profiled_tests()