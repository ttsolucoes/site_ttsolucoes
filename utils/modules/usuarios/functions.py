import hashlib
from typing import Dict, List, Optional, Union
from config.database import executar_sql

def _hash_senha(senha: str) -> str:
    """Gera um hash SHA-256 para a senha."""
    return hashlib.sha256(senha.encode()).hexdigest()

def ver_recuperaracesso_public() -> List[Dict[str, Union[int, str, bool]]]:
    """Retorna todos os usuários públicos (criados na parte pública) com suas informações."""
    query = """
SELECT 
    usuario_id, 
    username, 
    email, 
    motivo
FROM recuperar_acesso
WHERE status == 'a validar';
    """
    resultados = executar_sql(query)
    
    return [{
        'id': row[0],
        'username': row[1],
        'email': row[2],
        'motivo': row[3]
    } for row in resultados]

def ver_usuarios_public() -> List[Dict[str, Union[int, str, bool]]]:
    """Retorna todos os usuários públicos (criados na parte pública) com suas informações."""
    query = """
SELECT 
    id, 
    username, 
    email, 
    senha
FROM novos_usuarios
    """
    resultados = executar_sql(query)
    
    return [{
        'id': row[0],
        'username': row[1],
        'email': row[2],
        'senha': row[3]
    } for row in resultados]

def ver_usuarios() -> List[Dict[str, Union[int, str, bool]]]:
    """Retorna todos os usuários com suas informações."""
    query = """
SELECT 
    u.id, 
    u.username, 
    u.senha_hash,
    u.email,
    u.cargo,
    u.acesso_api,
    COUNT(l.id) as total_logs
FROM usuarios u
LEFT JOIN logs_usuarios l ON u.id = l.usuario_id
GROUP BY u.id
    """
    resultados = executar_sql(query)
    
    return [{
        'id': row[0],
        'username': row[1],
        'senha': "********",
        'email': row[3],
        'cargo': row[4],
        'acesso_api': bool(row[5]),
        'total_logs': row[6]
    } for row in resultados]

def criar_usuario_public(username: str, senha: str, email : str) -> bool:

    query = f"""
INSERT INTO novos_usuarios (username, email, senha)
VALUES ('{username}', '{email}', '{senha}');
    """
    try:
        executar_sql(query)

        # Registrar log
        user_id = 0
        log_query = f"""
INSERT INTO logs_usuarios (usuario_id, acao, detalhes)
VALUES ({user_id}, 'solicitacao_user', 'Solicitacao da criacao do usuario {username}')
        """
        executar_sql(log_query)

        return True
    except Exception:
        return False

def recuperar_acesso_public(conta: str, motivo) -> bool:

    if '@' in conta:
        campo = 'email'
        registro = conta
        motivo = motivo
    else:
        campo = 'username'
        registro = conta
        motivo = motivo

    query = f"""
INSERT INTO recuperar_acesso ({campo}, motivo)
VALUES ('{registro}', '{motivo}');
    """
    try:
        executar_sql(query)

        # Registrar log
        user_id = 0
        log_query = f"""
INSERT INTO logs_usuarios (usuario_id, acao, detalhes)
VALUES ({user_id}, 'solicitacao_user', 'Solicitacao para recuperacao da conta do usuario {conta}')
        """
        executar_sql(log_query)

        return True
    except Exception:
        return False

def detalhar_recuperar_acesso( id_solicitacao : int ) -> List[Dict[str, Union[int, str]]]:
    """Retorna todos os registros de recuperação de acesso."""
    query = f"""
SELECT * FROM recuperar_acesso WHERE usuario_id = {id_solicitacao};
    """
    res = executar_sql(query)
    if not res:
        return {}
    resultado = {
        'id': res[0][0],
        'user': res[0][1],
        'email': res[0][2],
        'motivo': res[0][3],
        'data': res[0][5]
    }
    return resultado

def criar_usuario(username: str, email, senha: str, cargo: str = 'user', acesso_api: bool = False) -> bool:

    senha_hash = _hash_senha(senha)
    query = f"""
INSERT INTO usuarios (username, email, senha_hash, cargo, acesso_api)
VALUES ('{username}', '{email}', '{senha_hash}', '{cargo}', {int(acesso_api)})
    """
    try:
        executar_sql(query)
        
        user_id = executar_sql(f"SELECT id FROM usuarios WHERE username = '{username}'")[0][0]
        log_query = f"""
INSERT INTO logs_usuarios (usuario_id, acao, detalhes)
VALUES ({user_id}, 'criacao', 'Usuário criado com cargo {cargo}')
        """
        executar_sql(log_query)
        return True
    except Exception:
        return False

def aprovar_usuario_publico(username: str) -> bool:
    """Move usuário da tabela pública para privada"""
    try:

        usuario = executar_sql(f"SELECT * FROM novos_usuarios WHERE username = '{username}'")[0]
        criar_usuario(usuario[1], usuario[2], usuario[3], 'user', -1, False)
        executar_sql(f"DELETE FROM novos_usuarios WHERE username = '{username}'")
        
        return True
    except Exception as e:
        return False

def remover_usuario(username: str, tipo: str) -> bool:
    """Remove usuário especificando se é público ou privado"""
    try:
        if tipo == 'publicos':
            query = f"DELETE FROM novos_usuarios WHERE username = '{username}'"
            print(executar_sql(query))
        else:
            user_id = executar_sql(f"SELECT id FROM usuarios WHERE username = '{username}'")[0][0]
            executar_sql(f"DELETE FROM logs_usuarios WHERE usuario_id = {user_id}")
            executar_sql(f"DELETE FROM usuarios WHERE username = '{username}'")
        
        return True
    except Exception:
        return False

def log_usuario(username: str) -> List[Dict[str, Union[str, int]]]:
    """Retorna os logs de um usuário específico."""
    query = f"""
SELECT l.acao, l.detalhes, l.data_hora
FROM logs_usuarios l
JOIN usuarios u ON l.usuario_id = u.id
WHERE u.username = '{username}'
ORDER BY l.data_hora DESC
    """
    resultados = executar_sql(query)
    
    return [{
        'acao': row[0],
        'detalhes': row[1],
        'data_hora': row[2]
    } for row in resultados]

def validar_acesso(username: str, senha: str) -> bool:
    """Valida as credenciais de um usuário."""
    senha_hash = _hash_senha(senha)
    query = f"""
SELECT 1 FROM usuarios 
WHERE username = '{username}' AND senha_hash = '{senha_hash}'
    """
    resultado = executar_sql(query)
    return len(resultado) > 0

def inserir_log(username: str, acao: str, detalhes: str = None) -> bool:
    """Insere um log de ação do usuário."""
    try:
        user_query = f"SELECT id FROM usuarios WHERE username = '{username}'"
        user_result = executar_sql(user_query)
        
        if not user_result:
            return False
            
        user_id = user_result[0][0]

        log_query = f"""
INSERT INTO logs_usuarios (usuario_id, acao, detalhes)
VALUES ({user_id}, '{acao}', {f"'{detalhes}'" if detalhes else 'NULL'})
        """
        
        executar_sql(log_query)
        return True
        
    except Exception as e:
        return False

def detalhar_usuario(username: str) -> Optional[Dict[str, Union[int, str, bool]]]:
    """Retorna os detalhes de um usuário específico."""
    query = f"""
SELECT 
    u.id, 
    u.username, 
    u.email, 
    u.cargo, 
    u.acesso_api
FROM usuarios u
WHERE u.username = '{username}'
    """
    try:
        resultado = executar_sql(query)
        if not resultado:
            return None
        
        row = resultado[0]
        return {
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'cargo': row[3],
            'acesso_api': bool(row[4])
        }
    except Exception:
        return None

def promover_usuario(username: str, tipo: str, novo_cargo: str = None, nova_senha: str = None) -> bool:
    try:
        if tipo == 'publico':
            query = f"""
INSERT INTO usuarios (username, email, senha, cargo)
SELECT username, email, senha, 'user'
FROM novos_usuarios 
WHERE username = '{username}';

DELETE FROM novos_usuarios 
WHERE username = '{username}';
            """
            executar_sql(query)

            # Obtem ID do novo usuário criado
            user_id = executar_sql(f"SELECT id FROM usuarios WHERE username = '{username}'")[0][0]

            log_query = f"""
INSERT INTO logs (user_id, tipo, detalhes)
VALUES ({user_id}, 'criacao', ''Usuário aprovado da fila pública com cargo user'')
            """
            executar_sql(log_query)
            return True

        elif tipo == 'privado' or tipo == 'internos':
            updates = []
            log_details = []

            if novo_cargo:
                updates.append(f"cargo = '{novo_cargo}'")
                log_details.append(f"cargo alterado para {novo_cargo}")

            if nova_senha:
                senha_hash = _hash_senha(nova_senha)
                updates.append(f"senha = '{senha_hash}'")
                log_details.append("senha alterada")

            if not updates:
                return False

            update_query = f"""
UPDATE usuarios 
SET {', '.join(updates)} 
WHERE username = '{username}';
            """
            executar_sql(update_query)

            user_id = executar_sql(f"SELECT id FROM usuarios WHERE username = '{username}'")[0][0]
            log_query = f"""
INSERT INTO logs (user_id, tipo, detalhes)
VALUES ({user_id}, 'promocao', '{', '.join(log_details)}')
            """
            executar_sql(log_query)
            return True

        else:
            raise ValueError("Tipo inválido. Use 'publico' ou 'privado'.")

    except Exception as e:
        return False

def atualizar_senha_usuario(username: str, nova_senha: str) -> bool:
    """Atualiza a senha de um usuário específico."""
    try:
        senha_hash = _hash_senha(nova_senha)
        query = f"""
        UPDATE usuarios 
        SET senha_hash = '{senha_hash}' 
        WHERE username = '{username}';
        """
        executar_sql(query)

        # Registrar log
        user_id = executar_sql(f"SELECT id FROM usuarios WHERE username = '{username}'")[0][0]
        log_query = f"""
        INSERT INTO logs_usuarios (usuario_id, acao, detalhes)
        VALUES ({user_id}, 'atualizacao_senha', 'Senha atualizada pelo suporte')
        """
        executar_sql(log_query)

        return True
    except Exception:
        return False

def atualizar_email_usuario(username: str, email: str) -> bool:
    """Atualiza a email de um usuário específico."""
    try:
        senha_hash = email
        query = f"""
        UPDATE usuarios 
        SET email = '{senha_hash}' 
        WHERE username = '{username}';
        """
        executar_sql(query)

        # Registrar log
        user_id = executar_sql(f"SELECT id FROM usuarios WHERE username = '{username}'")[0][0]
        log_query = f"""
        INSERT INTO logs_usuarios (usuario_id, acao, detalhes)
        VALUES ({user_id}, 'atualizacao_senha', 'Senha atualizada pelo suporte')
        """
        executar_sql(log_query)

        return True
    except Exception:
        return False

def acao_recuperar_acesso( username: str, id_solicitacao : int, tipo : str, nova_senha : str = None, creditos : int = -1 ) -> bool:

    if tipo == 'aprovar_senha':
        atualizar_senha_usuario(username, nova_senha)
        query = f"""
UPDATE recuperar_acesso SET status = 'finalizado' WHERE usuario_id = {id_solicitacao};
        """
        executar_sql(query)
        return True
    else:
        return False
