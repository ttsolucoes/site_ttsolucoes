import secrets

def gerar_chave_secreta(tamanho: int = 64) -> str:
    return secrets.token_hex(tamanho)

if __name__ == "__main__":
    chave = gerar_chave_secreta()
    print(f"Chave secreta gerada:\n{chave}")

