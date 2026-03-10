"""
TASK 5: DOCKER IMAGE OPTIMIZATION
---------------------------------
Description: Implementation of Multi-Stage Docker builds to optimize 
data science application environments.

Features: Automated benchmarking of image sizes, reducing footprint 
from ~1.5GB to ~500MB using slim variants and build-stage separation.

Stack: Python, Docker, Subprocess API.
"""


import subprocess
import time

def run_command(cmd , description):
    """Run a shell command and show output"""
    print(f"\n→ {description}")
    print(f"Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding ='utf-8',
            errors='replace'
        )
        print(result.stdout.strip())
        if result.stderr.strip():
            print("Warnings/Errors:", result.stderr.strip())
        return True
    except subprocess.CalledProcessError as e:
        print("!!! Command failed !!!")
        print("Exit code:", e.returncode)
        print("Error output:", e.stderr.strip())
        return False
    
def build_show_size(dockerfile, tag):
    print(f"\n{'='*65}")
    print(f"Building image: {tag}")
    print(f"Using: {dockerfile}")
    print('='*65)

    success = run_command(
        ["docker", "build", "-f", dockerfile, "-t", tag, "."],
        "Building image...")
    if not success:
        return False
    
    run_command(
        ["docker", "images", tag, "--format", "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"],
        "Image size:"
    )
    return True