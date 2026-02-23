import sqlite3


class Database:

    def __init__(self):
        self.conn = sqlite3.connect("estudos.db")
        self.conn.row_factory = sqlite3.Row
        self.criar_tabelas()

    # ==============================
    # CRIAÇÃO DAS TABELAS
    # ==============================

    def criar_tabelas(self):
        cursor = self.conn.cursor()

        # Tabela de disciplinas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS disciplinas (
            nome TEXT PRIMARY KEY,
            peso REAL,
            meta INTEGER DEFAULT 0,
            concluido INTEGER DEFAULT 0
        )
        """)

        # Tabela de configuração (horas por dia)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            horas_dia REAL
        )
        """)

        # Tabela de ciclos (histórico)
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

        # Tabela detalhada de disciplinas por ciclo
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
    # CONFIGURAÇÃO (HORAS POR DIA)
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