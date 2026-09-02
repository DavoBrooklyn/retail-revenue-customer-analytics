import subprocess
import sys


subprocess.run([sys.executable, "src/generate_data.py"], check=True)
subprocess.run([sys.executable, "src/analyze.py"], check=True)

