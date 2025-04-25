import sqlite3
from typing import Union
from typing import List
import pandas as pd
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar_banco():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except OperationalError as e:
        raise Exception(f"Erro ao conectar ao banco: {e}")

def finalizar_conexao(conn):
    try:
        if conn:
            conn.commit()
    except OperationalError as e:
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
            resultado = "Sucesso ao executar"
        conn.commit()
        return resultado
    except OperationalError as e:
        conn.rollback()
        raise Exception(f"Erro ao executar SQL: {e}")
    finally:
        cursor.close()
        conn.close()

def recriar_tabela(nome_tabela: str, colunas: List[str]):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        # Verificar se a tabela já existe
        cursor.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (nome_tabela,))
        tabela_existe = cursor.fetchone()[0]

        if tabela_existe:
            cursor.execute(f"DROP TABLE {nome_tabela}")

        colunas_sql = ", ".join([f"{col} TEXT" for col in colunas])
        cursor.execute(f"CREATE TABLE {nome_tabela} ({colunas_sql})")

        conn.commit()

    except OperationalError as e:
        conn.rollback()
        raise Exception(f"Erro ao recriar tabela: {e}")
    finally:
        cursor.close()
        conn.close()

def importar_dataframe_para_tabela(nome_tabela: str, colunas: List[str], df: pd.DataFrame):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        insert_sql = f"""
            INSERT INTO {nome_tabela} ({', '.join(colunas)}) 
            VALUES ({', '.join(['%s'] * len(colunas))})
            ON CONFLICT ({', '.join(colunas)}) DO NOTHING
        """
        for inicio in range(0, len(df), 1000):
            fim = inicio + 1000
            chunk = df.iloc[inicio:fim]
            dados = [tuple(map(str, linha)) for linha in chunk.values]
            cursor.executemany(insert_sql, dados)

        conn.commit()

    except OperationalError as e:
        conn.rollback()
        raise Exception(f"Erro ao importar dados: {e}")
    finally:
        cursor.close()
        conn.close()
