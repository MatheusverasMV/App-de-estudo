import math

class StudyModel:

    def __init__(self):
        self.disciplinas = {}
        self.horas_dia = 0

    def definir_horas_dia(self, horas):
        self.horas_dia = float(horas)

    def adicionar_disciplina(self, nome, peso):
        self.disciplinas[nome] = {
            "peso": float(peso),
            "meta": 0,
            "concluido": 0
        }

    def calcular_metas(self):
        horas_semana = self.horas_dia * 7
        soma_pesos = sum(d["peso"] for d in self.disciplinas.values())

        for nome, dados in self.disciplinas.items():
            meta = (dados["peso"] / soma_pesos) * horas_semana
            dados["meta"] = math.floor(meta + 0.5)

    def marcar_hora(self, nome):
        if nome in self.disciplinas:
            if self.disciplinas[nome]["concluido"] < self.disciplinas[nome]["meta"]:
                self.disciplinas[nome]["concluido"] += 1

    def todas_concluidas(self):
        return all(d["concluido"] >= d["meta"] for d in self.disciplinas.values())

    def resetar_semana(self):
        for dados in self.disciplinas.values():
            dados["concluido"] = 0

    def progresso_percentual(self, nome):
        d = self.disciplinas[nome]
        if d["meta"] == 0:
            return 0
        return (d["concluido"] / d["meta"]) * 100