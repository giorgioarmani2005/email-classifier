
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from config import settings

# setting очень полезная штука поэтому я стыбзил её и перенёс в корень проекта
