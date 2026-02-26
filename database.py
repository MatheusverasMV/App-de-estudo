import sqlite3
import os
import sys
from datetime import datetime


def caminho_banco():
    """
    Garante que o banco funcione corretamente
    tanto no modo desenvolvimento (.py)
    quanto no executável (.exe)
    """
    if getattr(sys, 'frozen', False):
        # Quando estiver rodando como .exe
        pasta = os.path.dirname(sys.executable)
    else:
        # Quando estiver rodando como script Python
        pasta = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(pasta, "estudos.db")


class Database:

    def __init__(self):
        self.conn = sqlite3.connect(caminho_banco())
        self.conn.row_factory = sqlite3.Row
        self.criar_tabelas()

    # ==============================
    # CRIAÇÃO DAS TABELAS
    # ==============================

    def criar_tabelas(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS disciplinas (
            nome TEXT PRIMARY KEY,
            peso REAL,
            meta INTEGER DEFAULT 0,
            concluido INTEGER DEFAULT 0
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            horas_dia REAL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ciclos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_inicio TEXT,
            data_fim TEXT,
            horas_dia REAL,
            total_meta INTEGER,
            total_concluido INTEGER,
            percentual REAL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ciclo_disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ciclo_id INTEGER,
            nome TEXT,
            meta INTEGER,
            concluido INTEGER,
            FOREIGN KEY (ciclo_id) REFERENCES ciclos(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS registro_diario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT UNIQUE,
            horas INTEGER DEFAULT 0
        )
        """)

        self.conn.commit()

    # ==============================
    # DISCIPLINAS
    # ==============================

    def inserir_disciplina(self, nome, peso):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO disciplinas (nome, peso)
            VALUES (?, ?)
        """, (nome, peso))
        self.conn.commit()

    def carregar_disciplinas(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM disciplinas")
        rows = cursor.fetchall()

        disciplinas = {}

        for row in rows:
            disciplinas[row["nome"]] = {
                "peso": row["peso"],
                "meta": row["meta"],
                "concluido": row["concluido"]
            }

        return disciplinas

    def atualizar_disciplina(self, nome, meta, concluido):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE disciplinas
            SET meta = ?, concluido = ?
            WHERE nome = ?
        """, (meta, concluido, nome))
        self.conn.commit()

    def deletar_disciplina(self, nome):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM disciplinas WHERE nome = ?", (nome,))
        self.conn.commit()

    def deletar_todas(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM disciplinas")
        self.conn.commit()

    def resetar_concluidos(self):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE disciplinas SET concluido = 0")
        self.conn.commit()

    # ==============================
    # CONFIGURAÇÃO
    # ==============================

    def salvar_horas_dia(self, horas):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO configuracoes (id, horas_dia)
            VALUES (1, ?)
            ON CONFLICT(id)
            DO UPDATE SET horas_dia = excluded.horas_dia
        """, (horas,))
        self.conn.commit()

    def carregar_horas_dia(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT horas_dia FROM configuracoes WHERE id = 1")
        row = cursor.fetchone()

        if row:
            return row["horas_dia"]
        return 0

    # ==============================
    # REGISTRO DIÁRIO (STREAK)
    # ==============================

    def registrar_estudo_hoje(self):
        hoje = datetime.now().strftime("%Y-%m-%d")
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO registro_diario (data, horas)
            VALUES (?, 1)
            ON CONFLICT(data)
            DO UPDATE SET horas = horas + 1
        """, (hoje,))

        self.conn.commit()

    def obter_datas_estudadas(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT data FROM registro_diario
            WHERE horas > 0
            ORDER BY data ASC
        """)
        rows = cursor.fetchall()
        return [row["data"] for row in rows]

    def obter_dias_estudados_intervalo(self, data_inicio, data_fim):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as total FROM registro_diario
            WHERE data BETWEEN ? AND ?
            AND horas > 0
        """, (data_inicio, data_fim))

        row = cursor.fetchone()
        return row["total"] if row else 0

    # ==============================
    # HISTÓRICO DE CICLOS
    # ==============================

    def salvar_ciclo(self, data_inicio, data_fim, horas_dia,
                     total_meta, total_concluido, percentual,
                     disciplinas):

        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO ciclos
            (data_inicio, data_fim, horas_dia,
             total_meta, total_concluido, percentual)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data_inicio, data_fim, horas_dia,
              total_meta, total_concluido, percentual))

        ciclo_id = cursor.lastrowid

        for nome, dados in disciplinas.items():
            cursor.execute("""
                INSERT INTO ciclo_disciplinas
                (ciclo_id, nome, meta, concluido)
                VALUES (?, ?, ?, ?)
            """, (ciclo_id,
                  nome,
                  dados["meta"],
                  dados["concluido"]))

        self.conn.commit()

    def listar_ciclos(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM ciclos
            ORDER BY id DESC
        """)
        return cursor.fetchall()

    def carregar_disciplinas_do_ciclo(self, ciclo_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT nome, meta, concluido
            FROM ciclo_disciplinas
            WHERE ciclo_id = ?
        """, (ciclo_id,))
        return cursor.fetchall()

    # ==============================
    # FECHAR CONEXÃO
    # ==============================

    def fechar(self):
        self.conn.close()