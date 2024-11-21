import subprocess
import os
from datetime import datetime
from pathlib import Path
import coverage
from .profiling_config import (
    PROFILE_OUTPUT_DIR,
    COVERAGE_SETTINGS
)

def run_comprehensive_profiling(services=None):
    """
    Run comprehensive profiling on specified services or all services.
    
    Args:
        services (list): List of service names to profile. If None, profiles all services.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = PROFILE_OUTPUT_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup coverage
    cov = coverage.Coverage(**COVERAGE_SETTINGS)
    cov.start()

    try:
        # Run tests with profiling
        test_command = ["pytest", "--profile"]
        if services:
            test_command.extend([f"tests/test_{service}_service.py" for service in services])
        
        subprocess.run(test_command)

        # Generate coverage report
        cov.stop()
        cov.save()
        cov.html_report(directory=output_dir / 'coverage')

        # Run memory profiling
        for service in services or ['customer', 'inventory', 'sales', 'reviews', 'analytics']:
            subprocess.run([
                "mprof", "run",
                "--output", str(output_dir / f"{service}_memory.dat"),
                f"services/{service}/{service}_service.py"
            ])

        # Generate memory profile plots
        for dat_file in output_dir.glob("*_memory.dat"):
            subprocess.run([
                "mprof", "plot",
                "--output", str(dat_file.with_suffix('.png')),
                str(dat_file)
            ])

        print(f"Profiling results saved to: {output_dir}")

    finally:
        if cov._started:
            cov.stop()

if __name__ == "__main__":
    run_comprehensive_profiling()