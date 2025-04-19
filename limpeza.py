import os
import shutil

path_raiz = os.path.abspath(os.path.join(__file__, '..'))
def limpar_cache( path_raiz : str ):
    for root, dirs, files in os.walk(path_raiz):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
            except Exception as e:
                pass
            finally:
                pass

limpar_cache(path_raiz)
print("Limpeza concluída com sucesso.")
