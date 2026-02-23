import sqlite3

DB_NAME = "estudos.db"


class Database:

    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.criar_tabelas()

    # ================== TABELAS ================== #

    def criar_tabelas(self):

        # Tabela disciplinas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS disciplinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                peso REAL NOT NULL,
                meta REAL NOT NULL,
                concluido REAL NOT NULL
            )
        """)

        # Tabela configurações
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY,
                horas_dia REAL
            )
        """)

        self.conn.commit()

    # ================== DISCIPLINAS ================== #

    def inserir_disciplina(self, nome, peso, meta=0, concluido=0):
        self.cursor.execute("""
            INSERT OR IGNORE INTO disciplinas (nome, peso, meta, concluido)
            VALUES (?, ?, ?, ?)
        """, (nome, peso, meta, concluido))
        self.conn.commit()

    def atualizar_disciplina(self, nome, meta, concluido):
        self.cursor.execute("""
            UPDATE disciplinas
            SET meta=?, concluido=?
            WHERE nome=?
        """, (meta, concluido, nome))
        self.conn.commit()

    def deletar_disciplina(self, nome):
        self.cursor.execute("""
            DELETE FROM disciplinas WHERE nome=?
        """, (nome,))
        self.conn.commit()

    def deletar_todas(self):
        self.cursor.execute("DELETE FROM disciplinas")
        self.conn.commit()

    def carregar_disciplinas(self):
        self.cursor.execute("""
            SELECT nome, peso, meta, concluido FROM disciplinas
        """)
        dados = self.cursor.fetchall()

        disciplinas = {}

        for nome, peso, meta, concluido in dados:
            disciplinas[nome] = {
                "peso": peso,
                "meta": meta,
                "concluido": concluido
            }

        return disciplinas

    def resetar_concluidos(self):
        self.cursor.execute("UPDATE disciplinas SET concluido = 0")
        self.conn.commit()

    # ================== CONFIG ================== #

    def salvar_horas_dia(self, horas):
        self.cursor.execute("DELETE FROM configuracoes")
        self.cursor.execute("""
            INSERT INTO configuracoes (horas_dia)
            VALUES (?)
        """, (horas,))
        self.conn.commit()

    def carregar_horas_dia(self):
        self.cursor.execute("SELECT horas_dia FROM configuracoes LIMIT 1")
        resultado = self.cursor.fetchone()
        return resultado[0] if resultado else 0

    # ================== FECHAR ================== #

    def fechar(self):
        self.conn.close()