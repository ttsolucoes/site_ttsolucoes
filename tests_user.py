try:
    from config import pastas_necessarias, pacotes_necessarios, verificar_pacotes, verificar_pastas

    verificar_pastas(pastas_necessarias)
    verificar_pacotes(pacotes_necessarios)
except:
    import sys

    print(
        "Erro ao importar os módulos necessários. Verifique se o script está sendo executado corretamente."
    )
    sys.exit(0)

from utils import criar_usuario
import logging
from config import path_log, nome_log, setup_log, path_raiz, limpar_cache

logger = logging.getLogger(setup_log(nome_log, path_log))

print(criar_usuario('tt_solucoes', 'techttracksolucoes@gmail.com', '12345678', 'admin', 1))
print(criar_usuario('luiz.esquivel', 'luizesquivel.pontes@gmail.com', '12345678', 'admin', 1))
print("Teste de bases do usuario concluído com sucesso.")

limpar_cache(path_raiz, logger, nome_log)
print("Teste concluído com sucesso.")
