import os
import sys
from pathlib import Path

# Add the project root directory to Python's path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir)) 