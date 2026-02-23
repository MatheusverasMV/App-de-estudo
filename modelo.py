import math
from database import Database


class StudyModel:

    def __init__(self):

        # 🔥 Cria instância do banco
        self.db = Database()

        # Carrega dados do banco
        self.disciplinas = self.db.carregar_disciplinas()

        # Carrega horas salvas
        self.horas_dia = self.db.carregar_horas_dia()

    # ---------------- CONFIGURAÇÃO ---------------- #

    def definir_horas_dia(self, horas):
        self.horas_dia = float(horas)
        self.db.salvar_horas_dia(self.horas_dia)

    # ---------------- DISCIPLINAS ---------------- #

    def adicionar_disciplina(self, nome, peso):
        peso = float(peso)

        if nome not in self.disciplinas:
            self.disciplinas[nome] = {
                "peso": peso,
                "meta": 0,
                "concluido": 0
            }

            self.db.inserir_disciplina(nome, peso)

    def deletar_disciplina(self, nome):
        if nome in self.disciplinas:
            del self.disciplinas[nome]
            self.db.deletar_disciplina(nome)

    def deletar_todas(self):
        self.disciplinas.clear()
        self.db.deletar_todas()

    # ---------------- CÁLCULO DE METAS ---------------- #

    def calcular_metas(self):
        horas_semana = self.horas_dia * 7
        soma_pesos = sum(d["peso"] for d in self.disciplinas.values())

        if soma_pesos == 0:
            return

        for nome, dados in self.disciplinas.items():
            meta = (dados["peso"] / soma_pesos) * horas_semana
            meta_arredondada = math.floor(meta + 0.5)

            dados["meta"] = meta_arredondada

            self.db.atualizar_disciplina(
                nome,
                meta_arredondada,
                dados["concluido"]
            )

    # ---------------- MARCAR HORAS ---------------- #

    def marcar_hora(self, nome):

        if nome not in self.disciplinas:
            return False

        disciplina = self.disciplinas[nome]

        if disciplina["concluido"] >= disciplina["meta"]:
            return False

        disciplina["concluido"] += 1

        if disciplina["concluido"] > disciplina["meta"]:
            disciplina["concluido"] = disciplina["meta"]

        self.db.atualizar_disciplina(
            nome,
            disciplina["meta"],
            disciplina["concluido"]
        )

        return True

    # ---------------- RESET ---------------- #

    def resetar_horas(self):
        for nome in self.disciplinas:
            self.disciplinas[nome]["concluido"] = 0

        self.db.resetar_concluidos()

    # ---------------- PROGRESSO ---------------- #

    def progresso_percentual(self, nome):
        d = self.disciplinas[nome]

        if d["meta"] == 0:
            return 0

        percentual = (d["concluido"] / d["meta"]) * 100
        return min(percentual, 100)

    def progresso_total(self):

        total_meta = sum(d["meta"] for d in self.disciplinas.values())
        total_concluido = sum(d["concluido"] for d in self.disciplinas.values())

        if total_meta == 0:
            return 0

        percentual = (total_concluido / total_meta) * 100
        return min(percentual, 100)