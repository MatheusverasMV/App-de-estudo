import sqlite3

DB_NAME = "estudos.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            peso INTEGER NOT NULL,
            meta INTEGER NOT NULL,
            concluido INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- CRUD ---------------- #

def inserir_disciplina(nome, peso, meta=0, concluido=0):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO disciplinas (nome, peso, meta, concluido)
        VALUES (?, ?, ?, ?)
    """, (nome, peso, meta, concluido))

    conn.commit()
    conn.close()


def atualizar_disciplina(nome, meta, concluido):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE disciplinas
        SET meta=?, concluido=?
        WHERE nome=?
    """, (meta, concluido, nome))

    conn.commit()
    conn.close()


def carregar_disciplinas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT nome, peso, meta, concluido FROM disciplinas")
    dados = cursor.fetchall()

    conn.close()

    disciplinas = {}

    for nome, peso, meta, concluido in dados:
        disciplinas[nome] = {
            "peso": peso,
            "meta": meta,
            "concluido": concluido
        }

    return disciplinas


def resetar_concluidos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("UPDATE disciplinas SET concluido = 0")

    conn.commit()
    conn.close()