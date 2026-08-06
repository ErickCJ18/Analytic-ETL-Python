import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
os.environ.setdefault("DB_SERVER", "localhost")
os.environ.setdefault("DB_DATABASE", "testdb")
os.environ.setdefault("DB_TRUSTED_CONNECTION", "yes")
os.environ.setdefault("DATA_DIR", str(ROOT / "data"))
os.environ.setdefault("LOG_DIR", str(ROOT / "logs"))
