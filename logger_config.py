import logging
import logging.config
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo config.env
load_dotenv(Path("config.env"))

# Trata a rota default usando Path para aceitar a barra de divisão '/'
DEFAULT_LOG_DIR = Path("pms_xirico") / "logs"
LOG_DIR_VAL = os.getenv("LOG_DIR")

# Garante que LOG_DIR_VAL seja um Path antes de juntar com a pasta home
LOG_DIR_PATH = Path(LOG_DIR_VAL) if LOG_DIR_VAL else DEFAULT_LOG_DIR
LOG_DIR = Path.home() / LOG_DIR_PATH

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

# Cria a pasta de destino caso não exista
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE_PATH = LOG_DIR / "pms.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    # Formato das mensagens
    "formatters": {
        "detalhado": {
            "format": (
                "[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] "
                "- %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simples": {
            "format": "[%(levelname)s] %(asctime)s - %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    # Destinos dos logs
    "handlers": {
        # Saída no Terminal/Console
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "simples",
            "stream": "ext://sys.stdout",
        },
        
        # Arquivo Rotativo: máx 2 MB por arquivo, mantém 5 backups
        "arquivo": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": LOG_LEVEL,
            "formatter": "detalhado",
            "filename": str(LOG_FILE_PATH),
            "maxBytes": 2 * 1024 * 1024,  # 2 Megabytes
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    # Configuração do Logger Raiz
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console", "arquivo"],
    },
}


def setup_logging():
    """Aplica a configuração no logger raiz."""
    logging.config.dictConfig(LOGGING_CONFIG)