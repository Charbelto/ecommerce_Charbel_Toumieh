import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import subprocess
import coverage
import pytest
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
    # Set non-interactive backend for matplotlib
    plt.switch_backend('Agg')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(PROFILE_OUTPUT_DIR) / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize coverage with proper settings
    cov = coverage.Coverage(
        source=['services'],
        branch=True,
        data_file=str(output_dir / '.coverage'),
        config_file=True,
        include=['*/services/*'],
        omit=['*/tests/*', '*/migrations/*']
    )
    
    cov.start()

    try:
        # Get absolute path to .coveragerc
        coverage_config = str(Path(__file__).parent.parent / ".coveragerc")
        
        # Configure pytest arguments
        pytest_args = [
            "--cov-config", coverage_config,
            "--cov-report", "xml",
            "--cov-report", "term-missing",
            "--cov=services",  # Match the source setting in .coveragerc
            "tests"
        ]
        
        # Run pytest with coverage
        pytest.main(pytest_args)

        # Stop coverage properly
        cov.stop()
        cov.save()

        # Generate reports
        coverage_dir = output_dir / 'coverage'
        coverage_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            cov.html_report(directory=str(coverage_dir))
        except coverage.exceptions.NoDataError:
            print("Warning: No coverage data was collected during the test run")

        # Run memory profiling
        for service in services or ['customer', 'inventory', 'sales', 'reviews', 'analytics']:
            service_dir = Path(f"services/{service}")
            output_file = output_dir / f"{service}_memory.dat"
            
            run_memory_profiling(service_dir, output_file)

        # Generate combined plot after all services are profiled
        plt.figure(figsize=(10, 6))
        for dat_file in output_dir.glob("*_memory.dat"):
            try:
                # Read memory profile data
                timestamps = []
                memory_usage = []
                with open(dat_file, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('CMDLINE'):
                            parts = line.strip().split()
                            if parts[0] == 'MEM' and len(parts) == 3:
                                timestamps.append(float(parts[2]) - float(timestamps[0]) if timestamps else 0)
                                memory_usage.append(float(parts[1]))

                if timestamps and memory_usage:
                    plt.figure(figsize=(10, 6))
                    plt.plot(timestamps, memory_usage, marker='o')
                    plt.title(f'Memory Usage - {dat_file.stem.replace("_memory", "")}')
                    plt.xlabel('Time (seconds)')
                    plt.ylabel('Memory Usage (MiB)')
                    plt.grid(True)
                    plt.tight_layout()
                    
                    # Save plot
                    plt.savefig(dat_file.with_suffix('.png'))
                    plt.close()
            except Exception as e:
                print(f"Error generating plot for {dat_file}: {e}")
        plt.savefig(output_dir / 'memory_comparison.png')
        plt.close()

        print(f"Profiling results saved to: {output_dir}")

    finally:
        if cov._started:
            cov.stop()

def run_memory_profiling(service_dir, output_file):
    temp_file = service_dir / f"profile_{service_dir.name}.py"
    try:
        with open(temp_file, "w") as f:
            f.write(f"""
from services.{service_dir.name}.{service_dir.name}_service import app
if __name__ == '__main__':
    app
""")
        
        result = subprocess.run([
            "python", "-m", "memory_profiler",
            str(temp_file),
            "-o", str(output_file)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Warning: Memory profiling failed for {service_dir.name}")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"Error profiling {service_dir.name}: {str(e)}")
    finally:
        temp_file.unlink(missing_ok=True)

if __name__ == "__main__":
    run_comprehensive_profiling()