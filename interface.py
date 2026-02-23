import customtkinter as ctk
from tkinter import messagebox
from modelo import StudyModel
import persistencia
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
        self.root.title("Dashboard de Estudo")
        self.root.geometry("1200x750")

        self.model = StudyModel()

        # 🔥 Carrega dados salvos automaticamente
        dados_salvos = persistencia.carregar()
        if dados_salvos:
            self.model.disciplinas = dados_salvos

        self.criar_layout()
        self.atualizar()

    # ================= LAYOUT ================= #

    def criar_layout(self):

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=250)
        self.sidebar.pack(side="left", fill="y", padx=15, pady=15)

        self.entry_horas = ctk.CTkEntry(self.sidebar, placeholder_text="Horas por dia")
        self.entry_horas.pack(pady=10)

        self.entry_nome = ctk.CTkEntry(self.sidebar, placeholder_text="Disciplina")
        self.entry_nome.pack(pady=5)

        self.entry_peso = ctk.CTkEntry(self.sidebar, placeholder_text="Peso")
        self.entry_peso.pack(pady=5)

        ctk.CTkButton(self.sidebar, text="Adicionar", command=self.adicionar).pack(pady=5)
        ctk.CTkButton(self.sidebar, text="Calcular Metas", command=self.calcular).pack(pady=5)

        ctk.CTkButton(self.sidebar, text="Exportar PDF", command=self.exportar_pdf).pack(pady=30)

        # Área principal
        self.main = ctk.CTkFrame(self.root)
        self.main.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # 🔥 Dashboard superior
        self.dashboard_top = ctk.CTkFrame(self.main, height=120)
        self.dashboard_top.pack(fill="x", pady=(0, 15))

        self.label_total = ctk.CTkLabel(self.dashboard_top, text="", font=("Arial", 20, "bold"))
        self.label_total.pack(side="left", padx=30)

        self.label_percentual = ctk.CTkLabel(self.dashboard_top, text="", font=("Arial", 20))
        self.label_percentual.pack(side="left", padx=30)

        # Cards container
        self.cards_container = ctk.CTkScrollableFrame(self.main)
        self.cards_container.pack(fill="both", expand=True)

        # Gráfico
        self.frame_grafico = ctk.CTkFrame(self.main, height=250)
        self.frame_grafico.pack(fill="both", expand=True, pady=10)

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

        # 🔥 Salva automaticamente
        persistencia.salvar(self.model.disciplinas)

        # Limpa cards antigos
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        total_meta = 0
        total_concluido = 0

        for nome, dados in self.model.disciplinas.items():

            total_meta += dados["meta"]
            total_concluido += dados["concluido"]

            card = ctk.CTkFrame(self.cards_container, corner_radius=15)
            card.pack(fill="x", padx=20, pady=10)

            titulo = ctk.CTkLabel(
                card,
                text=nome,
                font=("Arial", 18, "bold")
            )
            titulo.pack(anchor="w", padx=20, pady=(15, 5))

            progresso = self.model.progresso_percentual(nome)

            barra = ctk.CTkProgressBar(card, height=15)
            barra.set(progresso / 100)
            barra.pack(fill="x", padx=20, pady=5)

            info = ctk.CTkLabel(
                card,
                text=f"{dados['concluido']}/{dados['meta']} horas ({int(progresso)}%)"
            )
            info.pack(anchor="w", padx=20)

            botao = ctk.CTkButton(
                card,
                text="+1 hora",
                width=120,
                command=lambda n=nome: self.marcar_hora_card(n)
            )
            botao.pack(anchor="e", padx=20, pady=15)

        # 🔥 Atualiza métricas superiores
        percentual_total = 0
        if total_meta > 0:
            percentual_total = (total_concluido / total_meta) * 100

        self.label_total.configure(
            text=f"Total: {total_concluido}/{total_meta} horas"
        )

        self.label_percentual.configure(
            text=f"Progresso Geral: {int(percentual_total)}%"
        )

        self.atualizar_grafico()

        # 🔥 Reset automático
        if self.model.todas_concluidas() and len(self.model.disciplinas) > 0:
            if messagebox.askyesno("Semana Concluída", "Deseja resetar para próxima semana?"):
                self.model.resetar_semana()
                self.atualizar()

    # ================= GRÁFICO ================= #

    def atualizar_grafico(self):

        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        fig = plt.Figure(figsize=(6, 3))
        ax = fig.add_subplot(111)

        nomes = []
        valores = []

        for nome in self.model.disciplinas:
            nomes.append(nome)
            valores.append(self.model.progresso_percentual(nome))

        ax.bar(nomes, valores)
        ax.set_ylim(0, 100)
        ax.set_ylabel("Progresso (%)")

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


# ================= EXECUÇÃO ================= #

if __name__ == "__main__":
    root = ctk.CTk()
    app = StudyApp(root)
    root.mainloop()