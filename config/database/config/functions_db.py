import sqlite3
from typing import Union
from typing import List
import pandas as pd

def conectar_banco() -> sqlite3.Connection:

    from config.models.paths import path_data_base
    import os

    path_db = os.path.join(path_data_base, 'tt_solucoes.db')

    try:
        conn = sqlite3.connect(path_db)
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Erro ao conectar ao banco: {e}")

def finalizar_conexao(conn: sqlite3.Connection):
    try:
        if conn.in_transaction:
            conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Erro ao tentar comitar ou fazer rollback: {e}")
    finally:
        conn.close()

def executar_sql(sql: str) -> Union[str, list]:
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        if cursor.description:
            resultado = cursor.fetchall()
        else:
            conn.commit()
            resultado = "Sucesso ao executar"
        return resultado
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Erro ao executar SQL: {e}")
    finally:
        cursor.close()
        conn.close()

def recriar_tabela(nome_tabela: str, colunas: List[str]):

    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:

        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{nome_tabela}'"
        )
        tabela_existe = cursor.fetchone() is not None

        if tabela_existe:
            cursor.execute(f"DROP TABLE {nome_tabela}")

        colunas_sql = ", ".join([f"{col} TEXT" for col in colunas])
        cursor.execute(f"CREATE TABLE {nome_tabela} ({colunas_sql})")

        conn.commit()

    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Erro ao importar dados: {e}")
    finally:
        cursor.close()
        conn.close()

def importar_dataframe_para_tabela( nome_tabela: str, colunas: List[str], df: pd.DataFrame ):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:

        insert_sql = f"INSERT OR IGNORE INTO {nome_tabela} ({', '.join(colunas)}) VALUES ({', '.join(['?'] * len(colunas))})"
        for inicio in range(0, len(df), 1000):
            fim = inicio + 1000
            chunk = df.iloc[inicio:fim]
            dados = [tuple(map(str, linha)) for linha in chunk.values]
            cursor.executemany(insert_sql, dados)

        conn.commit()

    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Erro ao importar dados: {e}")
    finally:
        cursor.close()
        conn.close()
