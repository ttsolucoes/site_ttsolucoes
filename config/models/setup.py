import logging
import os
import subprocess
import sys
import shutil

def instalar_pacotes_externos(pacote: str) -> None:
    try:
        os.system("python.exe -m pip install --upgrade pip")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar o pacote {pacote}: {e}")
        raise

def verificar_pacotes(pacotes: list) -> None:
    for pacote in pacotes:
        try:
            __import__(pacote)
        except ImportError:
            print(f"Pacote {pacote} não encontrado. Instalando...")
            instalar_pacotes_externos(pacote)

def setup_log(nome_base: str, path_log: str) -> None:
    logging.basicConfig(
        filename=os.path.join(path_log, f'{nome_base}.log'),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def verificar_pastas(pastas: list) -> str:
    for pasta in pastas:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
    return "Pastas verificadas e criadas, se necessário."

def limpar_cache( path_raiz : str, logger : logging.Logger, prefixo_log : str ):
    for root, dirs, files in os.walk(path_raiz):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                logger.info(f"{prefixo_log} >> limpar_cache >> Tentativa de deletar: {pycache_path}")
            except Exception as e:
                logger.error(f"{prefixo_log} >> limpar_cache >> Erro ao deletar {pycache_path}: {e}")
            finally:
                logger.info(f"{prefixo_log} >> limpar_cache >> Tentativa de deletar: {pycache_path} concluida")
