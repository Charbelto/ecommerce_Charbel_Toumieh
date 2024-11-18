import subprocess
import os
from datetime import datetime

def run_comprehensive_profiling():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"profiling_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Run tests with coverage
    subprocess.run(["coverage", "run", "-m", "pytest"])
    subprocess.run(["coverage", "html", "-d", f"{output_dir}/coverage"])
    
    # Run performance profiling
    subprocess.run([
        "python", "-m", "cProfile", 
        "-o", f"{output_dir}/profile.stats",
        "services/analytics/analytics_service.py"
    ])
    
    # Generate memory profile
    subprocess.run([
        "mprof", "run", 
        "--output", f"{output_dir}/memory_profile.dat",
        "services/analytics/analytics_service.py"
    ])
    
    # Generate memory profile plot
    subprocess.run([
        "mprof", "plot",
        "-o", f"{output_dir}/memory_profile.png",
        f"{output_dir}/memory_profile.dat"
    ])

if __name__ == "__main__":
    run_comprehensive_profiling()