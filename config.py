import logging


DB_NAME = 'currency.db'

# LOGGER_CONFIG = dict(level=logging.DEBUG,
#                      file='app.log',
#                      formatter=logging.Formatter("%(asctime)s [%(levelname)s] - %(name)s:%(message)s")
#                      )

HTTP_TIMEOUT = 15

IP_LIST = ["127.0.0.1", "127.0.0.10", "127.0.0.2", "127.115.99.211", "10.41.255.55"]

LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': "[%(asctime)s] [%(levelname)s] - %(name)s: %(message)s",
        },
    },

    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'new.log',
        },
    },
    'loggers': {
        'Currency': {
            'handlers': ['file', ],
            'level': logging.DEBUG
        },
        'Api': {
            'handlers': ['file', ],
            'level': logging.DEBUG
        },
        'Tasks': {
            'handlers': ['file', ],
            'level': logging.DEBUG
        },
    },
}
