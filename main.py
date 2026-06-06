"""Predator-Prey Fear Model
Entry point: python main.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

from pipeline import run_pipeline

if __name__ == '__main__':
    run_pipeline()