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
    "branch": True,
    "source": ["services", "utils"],
    "omit": [
        "*/tests/*",
        "*/migrations/*",
        "*/__init__.py"
    ]
}

# Database query profiling settings
DB_PROFILE_SETTINGS = {
    "slow_query_threshold": 100,  # ms
    "log_queries": True,
    "explain_analyze": True
}