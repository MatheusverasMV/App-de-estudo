from database import Database


class StudyModel:

    def __init__(self):
        self.db = Database()
        self.disciplinas = self.db.carregar_disciplinas()
        self.horas_dia = self.db.carregar_horas_dia()

    # ================= DISCIPLINAS ================= #

    def adicionar_disciplina(self, nome, peso):
        if nome in self.disciplinas:
            return

        self.db.inserir_disciplina(nome, peso)
        self.disciplinas[nome] = {
            "peso": peso,
            "meta": 0,
            "concluido": 0
        }

    def deletar_disciplina(self, nome):
        if nome not in self.disciplinas:
            return

        self.db.deletar_disciplina(nome)
        del self.disciplinas[nome]

    def deletar_todas(self):
        self.db.deletar_todas()
        self.disciplinas.clear()

    # ================= CONFIG ================= #

    def definir_horas_dia(self, horas):
        self.horas_dia = horas
        self.db.salvar_horas_dia(horas)

    # ================= METAS ================= #

    def calcular_metas(self):
        total_peso = sum(d["peso"] for d in self.disciplinas.values())

        if total_peso == 0:
            return

        for nome, dados in self.disciplinas.items():
            meta = (dados["peso"] / total_peso) * self.horas_dia * 7
            meta = round(meta, 2)

            dados["meta"] = meta
            self.db.atualizar_disciplina(nome, meta, dados["concluido"])

    # ================= HORAS ================= #

    def marcar_hora(self, nome):
        if nome not in self.disciplinas:
            return

        self.disciplinas[nome]["concluido"] += 1

        self.db.atualizar_disciplina(
            nome,
            self.disciplinas[nome]["meta"],
            self.disciplinas[nome]["concluido"]
        )

    def resetar_horas(self):
        for nome in self.disciplinas:
            self.disciplinas[nome]["concluido"] = 0

        self.db.resetar_concluidos()

    # ================= PROGRESSO ================= #

    def progresso_percentual(self, nome):
        dados = self.disciplinas[nome]

        if dados["meta"] == 0:
            return 0

        return (dados["concluido"] / dados["meta"]) * 100

    def progresso_total(self):
        total_meta = sum(d["meta"] for d in self.disciplinas.values())
        total_concluido = sum(d["concluido"] for d in self.disciplinas.values())

        if total_meta == 0:
            return 0

        return (total_concluido / total_meta) * 100