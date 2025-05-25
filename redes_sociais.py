import webbrowser
import threading
import customtkinter as ctk
from tkinter import messagebox

# Configurações iniciais
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

REDES_SOCIAIS = {
    "Facebook": "https://www.facebook.com",
    "Instagram": "https://www.instagram.com",
    "WhatsApp": "https://web.whatsapp.com",
    "Telegram": "https://web.telegram.org",
    "Twitter": "https://twitter.com",
}

class JanelaRedes(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Redes Sociais")
        self.geometry("420x340")
        self.resizable(False, False)
        self.configure(fg_color="#1a1a1a")

        self.botoes_redes = {}
        self.abas_ativas = set()  # redes marcadas como logadas

        ctk.CTkLabel(self, text="Redes Sociais", font=("Segoe UI", 20, "bold"), text_color="white").pack(pady=10)

        for nome, url in REDES_SOCIAIS.items():
            botao = ctk.CTkButton(
                self,
                text=nome,
                font=("Segoe UI", 14),
                command=lambda n=nome: self.abrir_ou_confirmar(n),
                fg_color="#2b2b2b",
                hover_color="#3b3b3b",
                corner_radius=10,
                width=200,
                height=40
            )
            botao.pack(pady=6)
            self.botoes_redes[nome] = botao

        self.label_status = ctk.CTkLabel(self, text="", text_color="lightgreen", font=("Segoe UI", 12))
        self.label_status.pack(pady=10)

    def abrir_ou_confirmar(self, nome_rede):
        url = REDES_SOCIAIS[nome_rede]

        if nome_rede in self.abas_ativas:
            # Já está "logada"? Confirmar se continua ativo
            resposta = messagebox.askyesno("Confirmação", f"Você ainda está logado no {nome_rede}?")
            if not resposta:
                self.abas_ativas.discard(nome_rede)
                self.resetar_botao(nome_rede)
                self.mostrar_notificacao(f"{nome_rede} desmarcado como logado.")
            else:
                self.mostrar_notificacao(f"{nome_rede} já está ativo.")
        else:
            threading.Thread(target=self.abrir_rede_social, args=(nome_rede, url), daemon=True).start()

    def abrir_rede_social(self, nome_rede, url):
        webbrowser.open_new_tab(url)

        resposta = messagebox.askyesno("Login", f"Você fez login no {nome_rede}?")
        if resposta:
            self.abas_ativas.add(nome_rede)
            self.destacar_botao(nome_rede)
            self.mostrar_notificacao(f"{nome_rede} logado e ativo.")
        else:
            self.mostrar_notificacao(f"{nome_rede} aberto, mas não marcado como logado.")

    def mostrar_notificacao(self, mensagem, erro=False):
        cor = "red" if erro else "lightgreen"
        self.label_status.configure(text=mensagem, text_color=cor)

    def destacar_botao(self, nome_ativo):
        botao = self.botoes_redes[nome_ativo]
        botao.configure(fg_color="#008000", hover_color="#006600")  # verde

    def resetar_botao(self, nome_rede):
        botao = self.botoes_redes[nome_rede]
        botao.configure(fg_color="#2b2b2b", hover_color="#3b3b3b")  # cor padrão

if __name__ == "__main__":
    app = JanelaRedes()
    app.mainloop()
