import customtkinter as ctk
from tkinter import messagebox
from modelo import StudyModel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class StudyApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Study SaaS Premium")
        self.root.geometry("1200x750")

        self.model = StudyModel()

        self.criar_layout()
        self.atualizar()

    # ================= LAYOUT ================= #

    def criar_layout(self):

        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=20)
        self.sidebar.pack(side="left", fill="y", padx=20, pady=20)

        ctk.CTkLabel(
            self.sidebar,
            text="Study SaaS",
            font=("Arial", 22, "bold")
        ).pack(pady=(20, 30))

        self.entry_horas = ctk.CTkEntry(self.sidebar, placeholder_text="Horas por dia")
        self.entry_horas.pack(pady=10, padx=20)

        self.entry_nome = ctk.CTkEntry(self.sidebar, placeholder_text="Disciplina")
        self.entry_nome.pack(pady=5, padx=20)

        self.entry_peso = ctk.CTkEntry(self.sidebar, placeholder_text="Peso")
        self.entry_peso.pack(pady=5, padx=20)

        ctk.CTkButton(self.sidebar, text="Adicionar", command=self.adicionar).pack(pady=5, padx=20)
        ctk.CTkButton(self.sidebar, text="Calcular Metas", command=self.calcular).pack(pady=5, padx=20)
        ctk.CTkButton(self.sidebar, text="Exportar PDF", command=self.exportar_pdf).pack(pady=40, padx=20)

        self.main = ctk.CTkFrame(self.root, corner_radius=20)
        self.main.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # KPI SUPERIOR
        self.kpi_frame = ctk.CTkFrame(self.main, corner_radius=20)
        self.kpi_frame.pack(fill="x", pady=(0, 20))

        self.kpi_total = ctk.CTkLabel(self.kpi_frame, text="", font=("Arial", 18))
        self.kpi_total.pack(side="left", padx=40, pady=20)

        self.kpi_percentual = ctk.CTkLabel(self.kpi_frame, text="", font=("Arial", 18))
        self.kpi_percentual.pack(side="left", padx=40)

        self.kpi_sugestao = ctk.CTkLabel(self.kpi_frame, text="", font=("Arial", 18, "bold"))
        self.kpi_sugestao.pack(side="right", padx=40)

        self.cards_container = ctk.CTkScrollableFrame(self.main, corner_radius=20)
        self.cards_container.pack(fill="both", expand=True)

        self.frame_grafico = ctk.CTkFrame(self.main, corner_radius=20, height=250)
        self.frame_grafico.pack(fill="both", expand=True, pady=20)

    # ================= AÇÕES ================= #

    def adicionar(self):
        nome = self.entry_nome.get()
        peso = self.entry_peso.get()

        if nome == "" or peso == "":
            return

        self.model.adicionar_disciplina(nome, peso)

        self.entry_nome.delete(0, "end")
        self.entry_peso.delete(0, "end")

        self.atualizar()

    def calcular(self):
        if self.entry_horas.get() == "":
            return

        self.model.definir_horas_dia(self.entry_horas.get())
        self.model.calcular_metas()
        self.atualizar()

    def marcar_hora_card(self, nome):
        self.model.marcar_hora(nome)
        self.atualizar()

    # ================= ATUALIZAÇÃO ================= #

    def atualizar(self):

        for widget in self.cards_container.winfo_children():
            widget.destroy()

        total_meta = 0
        total_concluido = 0

        disciplina_mais_atrasada = None
        menor_percentual = 101

        for nome, dados in self.model.disciplinas.items():

            total_meta += dados["meta"]
            total_concluido += dados["concluido"]

            progresso = self.model.progresso_percentual(nome)

            if progresso < menor_percentual and dados["meta"] > 0:
                menor_percentual = progresso
                disciplina_mais_atrasada = nome

            card = ctk.CTkFrame(self.cards_container, corner_radius=20)
            card.pack(fill="x", padx=20, pady=10)

            titulo = ctk.CTkLabel(card, text=nome, font=("Arial", 18, "bold"))
            titulo.pack(anchor="w", padx=20, pady=(15, 5))

            barra = ctk.CTkProgressBar(card, height=15)
            barra.set(progresso / 100 if dados["meta"] > 0 else 0)
            barra.pack(fill="x", padx=20, pady=5)

            info = ctk.CTkLabel(
                card,
                text=f"{dados['concluido']}/{dados['meta']} horas ({int(progresso)}%)"
            )
            info.pack(anchor="w", padx=20)

            botao = ctk.CTkButton(
                card,
                text="Marcar 1 hora",
                width=120,
                command=lambda n=nome: self.marcar_hora_card(n)
            )
            botao.pack(anchor="e", padx=20, pady=15)

        percentual_total = 0
        if total_meta > 0:
            percentual_total = (total_concluido / total_meta) * 100

        self.kpi_total.configure(
            text=f"Total: {total_concluido}/{total_meta}h"
        )

        self.kpi_percentual.configure(
            text=f"Progresso Geral: {int(percentual_total)}%"
        )

        if disciplina_mais_atrasada:
            self.kpi_sugestao.configure(
                text=f"📌 Foque agora em: {disciplina_mais_atrasada}"
            )
        else:
            self.kpi_sugestao.configure(text="")

        self.atualizar_grafico_donut()

        if self.model.todas_concluidas() and len(self.model.disciplinas) > 0:
            if messagebox.askyesno("Semana Concluída", "Deseja resetar para próxima semana?"):
                self.model.resetar_semana()
                self.atualizar()

    # ================= DONUT CHART ================= #

    def atualizar_grafico_donut(self):

        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        total_meta = sum(d["meta"] for d in self.model.disciplinas.values())
        total_concluido = sum(d["concluido"] for d in self.model.disciplinas.values())

        fig = plt.Figure(figsize=(4, 4))
        ax = fig.add_subplot(111)

        if total_meta == 0:
            ax.text(
                0.5, 0.5,
                "Sem dados ainda",
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=14,
                transform=ax.transAxes
            )
            ax.axis("off")
        else:
            restante = max(total_meta - total_concluido, 0)
            sizes = [total_concluido, restante]

            ax.pie(
                sizes,
                labels=["Concluído", "Restante"],
                autopct="%1.0f%%",
                wedgeprops=dict(width=0.4)
            )

        canvas = FigureCanvasTkAgg(fig, self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= PDF ================= #

    def exportar_pdf(self):

        doc = SimpleDocTemplate("relatorio.pdf")
        elementos = []
        estilos = getSampleStyleSheet()

        elementos.append(Paragraph("Relatório Semanal de Estudos", estilos["Title"]))
        elementos.append(Spacer(1, 0.5 * inch))

        lista = []
        for nome, dados in self.model.disciplinas.items():
            texto = f"{nome} - {dados['concluido']}/{dados['meta']} horas"
            lista.append(ListItem(Paragraph(texto, estilos["Normal"])))

        elementos.append(ListFlowable(lista))
        doc.build(elementos)

        messagebox.showinfo("PDF", "Relatório exportado com sucesso!")


if __name__ == "__main__":
    root = ctk.CTk()
    app = StudyApp(root)
    root.mainloop()