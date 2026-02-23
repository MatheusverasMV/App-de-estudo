import math
from datetime import datetime
from database import Database


class StudyModel:

    def __init__(self):

        # Instância do banco
        self.db = Database()

        # Carrega dados salvos
        self.disciplinas = self.db.carregar_disciplinas()
        self.horas_dia = self.db.carregar_horas_dia()

        # Marca início do ciclo atual
        self.data_inicio_ciclo = datetime.now().strftime("%Y-%m-%d")

    # ==============================
    # CONFIGURAÇÃO
    # ==============================

    def definir_horas_dia(self, horas):
        self.horas_dia = float(horas)
        self.db.salvar_horas_dia(self.horas_dia)

    # ==============================
    # DISCIPLINAS
    # ==============================

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

    # ==============================
    # CÁLCULO DE METAS
    # ==============================

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

    # ==============================
    # MARCAR HORAS
    # ==============================

    def marcar_hora(self, nome):

        if nome not in self.disciplinas:
            return False

        disciplina = self.disciplinas[nome]

        # 🔥 Limite de meta
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

    # ==============================
    # FINALIZAR CICLO
    # ==============================

    def finalizar_ciclo(self):

        data_fim = datetime.now().strftime("%Y-%m-%d")

        total_meta = sum(d["meta"] for d in self.disciplinas.values())
        total_concluido = sum(d["concluido"] for d in self.disciplinas.values())

        percentual = 0
        if total_meta > 0:
            percentual = (total_concluido / total_meta) * 100

        # 🔥 Salva snapshot do ciclo
        self.db.salvar_ciclo(
            data_inicio=self.data_inicio_ciclo,
            data_fim=data_fim,
            horas_dia=self.horas_dia,
            total_meta=total_meta,
            total_concluido=total_concluido,
            percentual=percentual,
            disciplinas=self.disciplinas
        )

        # 🔥 Reinicia ciclo
        self.resetar_horas()

        # Nova data de início
        self.data_inicio_ciclo = datetime.now().strftime("%Y-%m-%d")

    # ==============================
    # RESET
    # ==============================

    def resetar_horas(self):
        for nome in self.disciplinas:
            self.disciplinas[nome]["concluido"] = 0

        self.db.resetar_concluidos()

    # ==============================
    # PROGRESSO
    # ==============================

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

    # ==============================
    # HISTÓRICO 🔥 (NOVO)
    # ==============================

    def obter_historico(self):
        """
        Retorna lista de ciclos salvos
        """
        return self.db.listar_ciclos()

    def obter_disciplinas_do_ciclo(self, ciclo_id):
        """
        Retorna disciplinas de um ciclo específico
        """
        return self.db.carregar_disciplinas_do_ciclo(ciclo_id)