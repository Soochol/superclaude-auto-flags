#!/usr/bin/env python3
import sys
import subprocess

# Install dependencies if needed
try:
    import numpy
    print(f"✅ NumPy already installed: {numpy.__version__}")
except ImportError:
    print("Installing NumPy...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy
    print(f"✅ NumPy installed: {numpy.__version__}")

try:
    import yaml
    print(f"✅ PyYAML already installed: {yaml.__version__}")
except ImportError:
    print("Installing PyYAML...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyYAML"])
    import yaml
    print(f"✅ PyYAML installed: {yaml.__version__}")

print("Dependencies ready!")