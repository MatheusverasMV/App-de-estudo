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

    # ================= HOVER ================= #

    def aplicar_hover(self, widget, cor_normal="#1E293B", cor_hover="#2A3A4F"):

        def on_enter(event):
            widget.configure(fg_color=cor_hover)

        def on_leave(event):
            widget.configure(fg_color=cor_normal)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    # ================= KPI CARD ================= #

    def criar_kpi_card(self, parent, titulo, valor, subtitulo, cor="#1E293B"):

        card = ctk.CTkFrame(
            parent,
            corner_radius=18,
            fg_color=cor,
            border_width=1,
            border_color="#2E3A4F"
        )
        card.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        self.aplicar_hover(card, cor, "#2A3A4F")

        ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 28, "bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 14)
        ).pack()

        ctk.CTkLabel(
            card,
            text=subtitulo,
            font=("Arial", 12),
            text_color="gray"
        ).pack(pady=(0, 15))

        return card

    # ================= ANIMAÇÃO ================= #

    def animar_barra(self, barra, valor_final):

        passos = 20

        def animar(passo=0):
            if passo <= passos:
                valor_atual = (valor_final / passos) * passo
                barra.set(valor_atual)
                barra.after(15, lambda: animar(passo + 1))

        animar()

    # ================= LAYOUT ================= #

    def criar_layout(self):

        # ===== SIDEBAR ===== #
        self.sidebar = ctk.CTkFrame(
            self.root,
            width=260,
            corner_radius=0,
            fg_color="#0F172A"
        )
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar,
            text="STUDY PRO",
            font=("Arial", 22, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            self.sidebar,
            text="Painel de Performance",
            font=("Arial", 12),
            text_color="#94A3B8"
        ).pack(pady=(0, 30))

        divider = ctk.CTkFrame(self.sidebar, height=1, fg_color="#1E293B")
        divider.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            self.sidebar,
            text="PLANEJAMENTO",
            font=("Arial", 11, "bold"),
            text_color="#64748B"
        ).pack(anchor="w", padx=25, pady=(20, 10))

        self.entry_horas = ctk.CTkEntry(self.sidebar, placeholder_text="Horas por dia", height=40)
        self.entry_horas.pack(pady=5, padx=25, fill="x")

        self.entry_nome = ctk.CTkEntry(self.sidebar, placeholder_text="Disciplina", height=40)
        self.entry_nome.pack(pady=5, padx=25, fill="x")

        self.entry_peso = ctk.CTkEntry(self.sidebar, placeholder_text="Peso (importância)", height=40)
        self.entry_peso.pack(pady=5, padx=25, fill="x")

        ctk.CTkButton(
            self.sidebar,
            text="＋ Adicionar Disciplina",
            height=40,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.adicionar
        ).pack(pady=(15, 5), padx=25, fill="x")

        ctk.CTkButton(
            self.sidebar,
            text="⚡ Calcular Metas",
            height=40,
            fg_color="#0EA5E9",
            hover_color="#0284C7",
            command=self.calcular
        ).pack(pady=5, padx=25, fill="x")

        ctk.CTkLabel(
            self.sidebar,
            text="RELATÓRIOS",
            font=("Arial", 11, "bold"),
            text_color="#64748B"
        ).pack(anchor="w", padx=25, pady=(30, 10))

        ctk.CTkButton(
            self.sidebar,
            text="📄 Exportar PDF",
            height=40,
            fg_color="#334155",
            hover_color="#475569",
            command=self.exportar_pdf
        ).pack(pady=5, padx=25, fill="x")

        ctk.CTkLabel(
            self.sidebar,
            text="v1.0 Premium",
            font=("Arial", 10),
            text_color="#475569"
        ).pack(side="bottom", pady=20)

        # ===== MAIN ===== #
        self.main = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#0B1120")
        self.main.pack(side="right", fill="both", expand=True)

        self.kpi_frame = ctk.CTkFrame(self.main, corner_radius=20, fg_color="#0F172A")
        self.kpi_frame.pack(fill="x", padx=30, pady=(30, 20))

        self.cards_container = ctk.CTkScrollableFrame(self.main, corner_radius=20, fg_color="#0F172A")
        self.cards_container.pack(fill="both", expand=True, padx=30)

        self.frame_grafico = ctk.CTkFrame(self.main, corner_radius=20, fg_color="#0F172A")
        self.frame_grafico.pack(fill="both", expand=True, padx=30, pady=30)

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

        for widget in self.kpi_frame.winfo_children():
            widget.destroy()

        for widget in self.cards_container.winfo_children():
            widget.destroy()

        total_meta = 0
        total_concluido = 0

        for nome, dados in self.model.disciplinas.items():

            total_meta += dados["meta"]
            total_concluido += dados["concluido"]

            progresso = self.model.progresso_percentual(nome)

            card = ctk.CTkFrame(
                self.cards_container,
                corner_radius=20,
                fg_color="#1E293B",
                border_width=1,
                border_color="#2E3A4F"
            )
            card.pack(fill="x", padx=20, pady=10)

            self.aplicar_hover(card, "#1E293B", "#2A3A4F")

            ctk.CTkLabel(card, text=nome, font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=(15, 5))

            barra = ctk.CTkProgressBar(card, height=15)
            barra.pack(fill="x", padx=20, pady=5)

            if dados["meta"] > 0:
                self.animar_barra(barra, progresso / 100)
            else:
                barra.set(0)

            ctk.CTkLabel(
                card,
                text=f"{dados['concluido']}/{dados['meta']} horas ({int(progresso)}%)"
            ).pack(anchor="w", padx=20)

            ctk.CTkButton(
                card,
                text="＋ 1h",
                width=100,
                corner_radius=15,
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                command=lambda n=nome: self.marcar_hora_card(n)
            ).pack(anchor="e", padx=20, pady=15)

        percentual_total = 0
        if total_meta > 0:
            percentual_total = (total_concluido / total_meta) * 100

        self.criar_kpi_card(self.kpi_frame, "Horas Totais", f"{total_concluido}h", f"Meta: {total_meta}h")
        self.criar_kpi_card(self.kpi_frame, "Progresso Geral", f"{int(percentual_total)}%", "Desempenho geral")
        self.criar_kpi_card(self.kpi_frame, "Disciplinas", f"{len(self.model.disciplinas)}", "Ativas")

        self.atualizar_grafico_donut()

    # ================= DONUT ================= #

    def atualizar_grafico_donut(self):

        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        total_meta = sum(d["meta"] for d in self.model.disciplinas.values())
        total_concluido = sum(d["concluido"] for d in self.model.disciplinas.values())

        fig = plt.Figure(figsize=(4, 4))
        ax = fig.add_subplot(111)

        if total_meta == 0:
            ax.text(0.5, 0.5, "Sem dados ainda",
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=14,
                    transform=ax.transAxes)
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