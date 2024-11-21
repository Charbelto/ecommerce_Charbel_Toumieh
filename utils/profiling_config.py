from pathlib import Path

# Profiling output directory
PROFILE_OUTPUT_DIR = Path("profiling_results")

# Performance profiling settings
PERFORMANCE_SETTINGS = {
    "builtins": True,
    "sort_by": "cumulative",
    "output_limit": 20
}

# Memory profiling settings
MEMORY_SETTINGS = {
    "threshold": 100,  # MB
    "interval": 0.1,  # seconds
}

# Coverage settings
COVERAGE_SETTINGS = {
    "config_file": str(Path(__file__).parent.parent / ".coveragerc"),
    "data_file": str(Path(__file__).parent.parent / ".coverage"),
    "source": ["services"],  # Match source in .coveragerc
    "branch": True
}


# Database query profiling settings
DB_PROFILE_SETTINGS = {
    "slow_query_threshold": 100,  # ms
    "log_queries": True,
    "explain_analyze": True
}