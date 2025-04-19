import os

path_raiz = os.path.abspath(os.path.join(__file__, '..', '..', '..'))

path_api = os.path.join(path_raiz, 'api')
path_api_modules = os.path.join(path_api, 'modules')
path_api_routes = os.path.join(path_api, 'routes')

path_app = os.path.join(path_raiz, 'app')
path_app_modules = os.path.join(path_app, 'modules')
path_app_routes = os.path.join(path_app, 'routes')
path_app_static = os.path.join(path_app, 'static')
path_app_templates = os.path.join(path_app, 'templates')

path_bot = os.path.join(path_raiz, 'bot')
path_bot_database = os.path.join(path_bot, 'database')
path_bot_modules = os.path.join(path_bot, 'modules')
path_bot_settings = os.path.join(path_bot, 'settings')

path_config = os.path.join(path_raiz, 'config')
path_config_models = os.path.join(path_config, 'models')
path_config_database = os.path.join(path_config, 'database')

path_data = os.path.join(path_raiz, 'data')
path_data_base = os.path.join(path_data, 'base')
path_data_dados = os.path.join(path_data, 'dados')
path_data_dadoszip = os.path.join(path_data, 'dados_zip')
path_data_entrada = os.path.join(path_data, 'entrada')
path_data_saida = os.path.join(path_data, 'saida')

path_log = os.path.join(path_raiz, 'logs')

path_temp = os.path.join(path_raiz, 'temp')

path_tests = os.path.join(path_raiz, 'tests')
