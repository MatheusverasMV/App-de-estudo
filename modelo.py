import math
import database


class StudyModel:

    def __init__(self):
        # Garante que a tabela exista
        database.criar_tabela()

        # Carrega dados salvos do banco
        self.disciplinas = database.carregar_disciplinas()
        self.horas_dia = 0

    # ---------------- CONFIGURAÇÃO ---------------- #

    def definir_horas_dia(self, horas):
        self.horas_dia = float(horas)

    # ---------------- DISCIPLINAS ---------------- #

    def adicionar_disciplina(self, nome, peso):
        peso = float(peso)

        if nome not in self.disciplinas:
            self.disciplinas[nome] = {
                "peso": peso,
                "meta": 0,
                "concluido": 0
            }

            database.inserir_disciplina(nome, peso)

    # ---------------- CÁLCULO DE METAS ---------------- #

    def calcular_metas(self):
        horas_semana = self.horas_dia * 7

        soma_pesos = sum(d["peso"] for d in self.disciplinas.values())

        # 🔥 Evita divisão por zero (corrige erro do gráfico também)
        if soma_pesos == 0:
            return

        for nome, dados in self.disciplinas.items():
            meta = (dados["peso"] / soma_pesos) * horas_semana
            meta_arredondada = math.floor(meta + 0.5)

            dados["meta"] = meta_arredondada

            # Atualiza no banco
            database.atualizar_disciplina(
                nome,
                meta_arredondada,
                dados["concluido"]
            )

    # ---------------- MARCAR HORAS ---------------- #

    def marcar_hora(self, nome):
        if nome in self.disciplinas:
            if self.disciplinas[nome]["concluido"] < self.disciplinas[nome]["meta"]:
                self.disciplinas[nome]["concluido"] += 1

                # Salva automaticamente
                database.atualizar_disciplina(
                    nome,
                    self.disciplinas[nome]["meta"],
                    self.disciplinas[nome]["concluido"]
                )

    # ---------------- VERIFICAÇÕES ---------------- #

    def todas_concluidas(self):
        return all(
            d["concluido"] >= d["meta"]
            for d in self.disciplinas.values()
            if d["meta"] > 0
        )

    def resetar_semana(self):
        for nome in self.disciplinas:
            self.disciplinas[nome]["concluido"] = 0

        database.resetar_concluidos()

    def progresso_percentual(self, nome):
        d = self.disciplinas[nome]

        if d["meta"] == 0:
            return 0

        return (d["concluido"] / d["meta"]) * 100