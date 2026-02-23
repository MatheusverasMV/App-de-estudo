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
        self.atualizar_historico()

    # ================= LAYOUT ================= #

    def criar_layout(self):

        # ===== SIDEBAR =====
        self.sidebar = ctk.CTkFrame(
            self.root,
            width=280,
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
        ).pack(pady=(0, 20))

        self.entry_horas = ctk.CTkEntry(self.sidebar, placeholder_text="Horas por dia", height=40)
        self.entry_horas.pack(padx=25, pady=5, fill="x")

        self.entry_nome = ctk.CTkEntry(self.sidebar, placeholder_text="Disciplina", height=40)
        self.entry_nome.pack(padx=25, pady=5, fill="x")

        self.entry_peso = ctk.CTkEntry(self.sidebar, placeholder_text="Peso (importância)", height=40)
        self.entry_peso.pack(padx=25, pady=5, fill="x")

        ctk.CTkButton(
            self.sidebar,
            text="＋ Adicionar Disciplina",
            height=40,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.adicionar
        ).pack(padx=25, pady=(10, 5), fill="x")

        ctk.CTkButton(
            self.sidebar,
            text="⚡ Calcular Metas",
            height=40,
            fg_color="#0EA5E9",
            hover_color="#0284C7",
            command=self.calcular
        ).pack(padx=25, pady=5, fill="x")

        ctk.CTkButton(
            self.sidebar,
            text="🔄 Resetar Horas",
            height=40,
            fg_color="#7F1D1D",
            hover_color="#991B1B",
            command=self.resetar_horas
        ).pack(padx=25, pady=5, fill="x")

        ctk.CTkButton(
            self.sidebar,
            text="🏁 Finalizar Ciclo",
            height=40,
            fg_color="#059669",
            hover_color="#047857",
            command=self.finalizar_ciclo
        ).pack(padx=25, pady=5, fill="x")

        ctk.CTkButton(
            self.sidebar,
            text="❌ Excluir Todas",
            height=40,
            fg_color="#B91C1C",
            hover_color="#991B1B",
            command=self.excluir_todas
        ).pack(padx=25, pady=(0, 15), fill="x")

        ctk.CTkButton(
            self.sidebar,
            text="📄 Exportar PDF",
            height=40,
            fg_color="#334155",
            hover_color="#475569",
            command=self.exportar_pdf
        ).pack(padx=25, pady=(0, 20), fill="x")

        self.frame_grafico = ctk.CTkFrame(self.sidebar, fg_color="#0F172A")
        self.frame_grafico.pack(padx=10, pady=10, fill="both")

        # ===== MAIN =====
        self.main = ctk.CTkFrame(self.root, fg_color="#0B1120")
        self.main.pack(side="right", fill="both", expand=True)

        # ===== TABVIEW =====
        self.tabview = ctk.CTkTabview(
            self.main,
            fg_color="#0B1120", 
            segmented_button_fg_color="#0F172A",
            segmented_button_selected_color="#2563EB",
            segmented_button_unselected_color="#1E293B"                      
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_dashboard = self.tabview.add("Dashboard")
        self.tab_historico = self.tabview.add("Histórico")

        # ===== DASHBOARD =====
        self.kpi_frame = ctk.CTkFrame(self.tab_dashboard, corner_radius=20, fg_color="#0F172A")
        self.kpi_frame.pack(fill="x", padx=30, pady=(30, 20))

        self.cards_container = ctk.CTkScrollableFrame(
            self.tab_dashboard,
            corner_radius=20,
            fg_color="#0F172A"
        )
        self.cards_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # ===== HISTÓRICO =====
        self.frame_cards_historico = ctk.CTkFrame(self.tab_historico, corner_radius=20, fg_color="#0F172A")
        self.frame_cards_historico.pack(fill="x", padx=30, pady=(30, 20))

        self.frame_barra = ctk.CTkFrame(self.tab_historico, corner_radius=20, fg_color="#0F172A")
        self.frame_barra.pack(fill="both", padx=30, pady=10)

        self.frame_linha = ctk.CTkFrame(self.tab_historico, corner_radius=20, fg_color="#0F172A")
        self.frame_linha.pack(fill="both", expand=True, padx=30, pady=(10, 30))

    # ================= VALIDAÇÃO ================= #

    def validar_numero(self, valor, campo):
        try:
            return float(valor)
        except:
            messagebox.showerror("Erro", f"{campo} deve ser um número válido.")
            return None

    # ================= AÇÕES ================= #

    def adicionar(self):
        nome = self.entry_nome.get()
        peso = self.entry_peso.get()

        if nome == "" or peso == "":
            return

        peso_validado = self.validar_numero(peso, "Peso")
        if peso_validado is None:
            return

        self.model.adicionar_disciplina(nome, peso_validado)
        self.entry_nome.delete(0, "end")
        self.entry_peso.delete(0, "end")
        self.atualizar()

    def calcular(self):
        horas = self.entry_horas.get()

        if horas == "":
            return

        horas_validada = self.validar_numero(horas, "Horas por dia")
        if horas_validada is None:
            return

        self.model.definir_horas_dia(horas_validada)
        self.model.calcular_metas()
        self.atualizar()

    def resetar_horas(self):
        confirmar = messagebox.askyesno(
            "Confirmar Reset",
            "Deseja realmente zerar todas as horas concluídas?"
        )

        if confirmar:
            self.model.resetar_horas()
            self.atualizar()

    def finalizar_ciclo(self):
        confirmar = messagebox.askyesno(
            "Finalizar Ciclo",
            "Deseja finalizar o ciclo atual?\n\n"
            "Isso irá salvar o histórico e zerar as horas concluídas."
        )

        if confirmar:
            try:
                self.model.finalizar_ciclo()
                messagebox.showinfo("Ciclo Finalizado", "Ciclo salvo no histórico com sucesso!")
                self.atualizar()
                self.atualizar_historico()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def excluir_disciplina(self, nome):
        confirmar = messagebox.askyesno(
            "Excluir Disciplina",
            f"Deseja excluir a disciplina '{nome}'?"
        )

        if confirmar:
            self.model.deletar_disciplina(nome)
            self.atualizar()

    def excluir_todas(self):
        confirmar = messagebox.askyesno(
            "Excluir Todas",
            "Deseja excluir TODAS as disciplinas?"
        )

        if confirmar:
            self.model.deletar_todas()
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

        percentual_total = self.model.progresso_total()

        total_meta = sum(d["meta"] for d in self.model.disciplinas.values())
        total_concluido = sum(d["concluido"] for d in self.model.disciplinas.values())

        self.criar_kpi_card(self.kpi_frame, "Horas Totais", f"{total_concluido}h", f"Meta: {total_meta}h")
        self.criar_kpi_card(self.kpi_frame, "Progresso Geral", f"{int(percentual_total)}%", "Desempenho geral")
        self.criar_kpi_card(self.kpi_frame, "Disciplinas", f"{len(self.model.disciplinas)}", "Ativas")

        for nome, dados in self.model.disciplinas.items():

            progresso = self.model.progresso_percentual(nome)

            card = ctk.CTkFrame(
                self.cards_container,
                corner_radius=20,
                fg_color="#1E293B",
                border_width=1,
                border_color="#2E3A4F"
            )
            card.pack(fill="x", padx=20, pady=10)

            top_frame = ctk.CTkFrame(card, fg_color="transparent")
            top_frame.pack(fill="x", padx=10, pady=(10, 0))

            ctk.CTkLabel(top_frame, text=nome, font=("Arial", 18, "bold")).pack(side="left")

            ctk.CTkButton(
                top_frame,
                text="✕",
                width=35,
                height=28,
                fg_color="#B91C1C",
                hover_color="#991B1B",
                command=lambda n=nome: self.excluir_disciplina(n)
            ).pack(side="right")

            barra = ctk.CTkProgressBar(card, height=15)
            barra.pack(fill="x", padx=20, pady=10)
            barra.set(progresso / 100 if dados["meta"] > 0 else 0)

            ctk.CTkLabel(
                card,
                text=f"{dados['concluido']}/{dados['meta']} horas ({int(progresso)}%)"
            ).pack(anchor="w", padx=20)

            ctk.CTkButton(
                card,
                text="＋ 1h",
                width=100,
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                command=lambda n=nome: self.marcar_hora_card(n)
            ).pack(anchor="e", padx=20, pady=15)

        self.atualizar_grafico_donut(percentual_total)

    # ================= DONUT ================= #

    def atualizar_grafico_donut(self, percentual):

        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        if percentual == 100:
            cor = "#38BDF8"
        elif percentual <= 25:
            cor = "#DC2626"
        elif percentual <= 50:
            cor = "#FACC15"
        else:
            cor = "#16A34A"

        restante = max(0, 100 - percentual)

        fig = plt.Figure(figsize=(3, 3), facecolor="#0F172A")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#0F172A")

        ax.pie(
            [percentual, restante],
            colors=[cor, "#1E293B"],
            startangle=90,
            wedgeprops=dict(width=0.4)
        )

        ax.text(0, 0, f"{int(percentual)}%",
                ha="center", va="center",
                fontsize=18, color="white")

        canvas = FigureCanvasTkAgg(fig, self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack()

    # ================= KPI ================= #

    def criar_kpi_card(self, parent, titulo, valor, subtitulo):

        card = ctk.CTkFrame(parent, corner_radius=18, fg_color="#1E293B")
        card.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(card, text=valor, font=("Arial", 28, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(card, text=titulo, font=("Arial", 14)).pack()
        ctk.CTkLabel(card, text=subtitulo, font=("Arial", 12), text_color="gray").pack(pady=(0, 15))

    # ================= HISTÓRICO ================= #

    def atualizar_historico(self):

        for widget in self.frame_cards_historico.winfo_children():
            widget.destroy()

        for widget in self.frame_barra.winfo_children():
            widget.destroy()

        for widget in self.frame_linha.winfo_children():
            widget.destroy()

        ciclos = self.model.obter_historico()

        if not ciclos:
            ctk.CTkLabel(
                self.frame_barra,
                text="📊 Você ainda não finalizou nenhum ciclo.\nFinalize seu primeiro ciclo para visualizar sua evolução!",
                font=("Arial", 16)
            ).pack(pady=40)
            return

        percentuais = [c["percentual"] for c in ciclos]
        total_ciclos = len(percentuais)
        media = sum(percentuais) / total_ciclos
        melhor = max(percentuais)
        ultimo = percentuais[0]

        self.criar_kpi_card(self.frame_cards_historico, "Total Ciclos", total_ciclos, "Ciclos finalizados")
        self.criar_kpi_card(self.frame_cards_historico, "Média Geral", f"{int(media)}%", "Desempenho médio")
        self.criar_kpi_card(self.frame_cards_historico, "Melhor Ciclo", f"{int(melhor)}%", "Maior percentual")
        self.criar_kpi_card(self.frame_cards_historico, "Último Ciclo", f"{int(ultimo)}%", "Ciclo mais recente")

        fig_bar = plt.Figure(figsize=(8, 4), facecolor="#0F172A")
        ax_bar = fig_bar.add_subplot(111)
        ax_bar.set_facecolor("#0F172A")

        labels = [f"C{len(percentuais)-i}" for i in range(len(percentuais))]
        ax_bar.bar(labels, percentuais)

        ax_bar.set_title("Comparação entre Ciclos", color="white")
        ax_bar.tick_params(colors="white")
        ax_bar.set_ylabel("Percentual (%)", color="white")

        canvas_bar = FigureCanvasTkAgg(fig_bar, self.frame_barra)
        canvas_bar.draw()
        canvas_bar.get_tk_widget().pack()

        percentuais_ordenados = list(reversed(percentuais))

        fig_line = plt.Figure(figsize=(8, 4), facecolor="#0F172A")
        ax_line = fig_line.add_subplot(111)
        ax_line.set_facecolor("#0F172A")

        ax_line.plot(range(1, len(percentuais_ordenados)+1), percentuais_ordenados, marker="o")

        ax_line.set_title("Evolução de Desempenho", color="white")
        ax_line.tick_params(colors="white")
        ax_line.set_ylabel("Percentual (%)", color="white")
        ax_line.set_xlabel("Ciclo", color="white")

        canvas_line = FigureCanvasTkAgg(fig_line, self.frame_linha)
        canvas_line.draw()
        canvas_line.get_tk_widget().pack()

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