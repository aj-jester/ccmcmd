import logging
import logging.config
import sys

log = logging.getLogger(__name__)
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },

    "handlers": {
        "console_stdout": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },

        "ccm_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "/var/log/ccmcmd.log",
            "maxBytes": 10485760,
            "backupCount": 14,
            "encoding": "utf8"
        }
    },

    "root": {
        "level": "DEBUG",
        "handlers": ["console_stdout", "ccm_file_handler"]
    }
})

def info(message):
    log.info(message)

def error(message, exit=True):
    log.error(message)

    if exit:
        sys.exit(1)

def debug(message):
    log.debug(message)
