from .paths import (
    path_log, path_temp, path_tests
)

pastas_necessarias = list()
pastas_necessarias.append(path_tests)
pastas_necessarias.append(path_temp)
pastas_necessarias.append(path_log)

pacotes_necessarios : list = [
    'sys',
    'subprocess',
    'logging',
    'os',
    'mysql',
    'mysql.connector',
    'db-sqlite3',
    'python-dotenv',
    'requests',
    'pandas',
    'bs4',
    're',
    'wget',
    'glob',
    'sqlite3'
]

nome_log = "tt_solucoes"
prefixo_log = "tt_solucoes >> "
