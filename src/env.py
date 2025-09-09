import os

# Base directory do projeto
BASE_DIR_LOCAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = os.getenv("BASE_DIR", BASE_DIR_LOCAL)

# Diretórios "simulando" o S3
BRONZE_PATH_LOCAL = os.path.join(BASE_DIR, "armazenamento", "01.bronze")
SILVER_PATH_LOCAL = os.path.join(BASE_DIR, "armazenamento", "02.silver")
GOLD_PATH_LOCAL = os.path.join(BASE_DIR, "armazenamento", "03.gold")

BRONZE_CONFIG_LOCAL = os.path.join(BASE_DIR, "assets", "01.bronze")
SILVER_CONFIG_LOCAL = os.path.join(BASE_DIR, "assets", "02.silver")
GOLD_CONFIG_LOCAL = os.path.join(BASE_DIR, "assets", "03.gold")

BRONZE_PATH = os.getenv("BRONZE_PATH", BRONZE_PATH_LOCAL)
SILVER_PATH = os.getenv("SILVER_PATH", SILVER_PATH_LOCAL)
GOLD_PATH = os.getenv("GOLD_PATH", GOLD_PATH_LOCAL)

# Criação dos diretórios, se não existirem
os.makedirs(BRONZE_PATH, exist_ok=True)
os.makedirs(SILVER_PATH, exist_ok=True)
os.makedirs(GOLD_PATH, exist_ok=True)

