import os
import sys
import subprocess
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
import wikipedia
import threading
import datetime
import pyperclip
import webbrowser

# Importe seus outros módulos aqui
try:
    from redes_sociais import JanelaRedes
    from gui.vids import App
    from abrir_dashboard import abrir_dashboard_streamlit # Se for uma função ou classe
    from media.MR import JanelaRadio
    from utils.web_search_manager import WebSearchManager
except ImportError as e:
    print(f"Erro ao importar um dos módulos: {e}")
    print("Certifique-se de que os arquivos 'redes_sociais.py', 'vids.py', 'abrir_dashboard.py', 'media/MR.py' e 'web_search_manager.py' estão nos diretórios corretos.")
    # Adicione tratamento de erro ou desabilite funcionalidades se os módulos não forem encontrados
    JanelaRedes = None
    App = None
    abrir_dashboard_streamlit = None
    JanelaRadio = None
    WebSearchManager = None


class JanelaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("DM Programação Tela Inteligente")
        ctk.set_appearance_mode("dark")

        self.web_search_manager = WebSearchManager() if 'WebSearchManager' in globals() else None

        # --- Imagem de Fundo ---
        self.fundo_label = None
        self.imagem_pil_fundo = None
        self.tk_image_fundo = None
        self._carregar_imagem_fundo()



        # Garante que os componentes da interface fiquem por cima do fundo
        self._organizar_camadas_ui()
        
        # Inicializa todos os componentes visuais
        self._inicializar_componentes_visuais()

        # Configura eventos de redimensionamento
        self.bind("<Configure>", self.on_resize)
        
        # Referências para janelas secundárias
        self.janela_redes = None
        self.musica_window = None
        self.videos_window = None
        
        # Importa a classe App do vids.py
        from gui.vids import App

    def _carregar_imagem_fundo(self):
        """Carrega a imagem de fundo e cria o label com tratamento de erros robusto."""
        try:
            caminho_imagem = os.path.join(os.path.dirname(__file__), "atlas.jpg")
            
            # Verifica se o arquivo existe e é uma imagem válida
            if not os.path.exists(caminho_imagem):
                raise FileNotFoundError(f"Imagem de fundo não encontrada em {caminho_imagem}")
                
            # Verifica se o arquivo é uma imagem válida
            try:
                with Image.open(caminho_imagem) as img:
                    img.verify()
                
                # Se passou na verificação, carrega a imagem
                self.imagem_pil_fundo = Image.open(caminho_imagem)
                
                # Cria o label de fundo
                self.fundo_label = ctk.CTkLabel(self, text="")
                self.fundo_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.fundo_label.lower()
                
            except (IOError, Image.UnidentifiedImageError) as img_error:
                raise ValueError(f"Arquivo de imagem inválido: {img_error}")
                
        except Exception as e:
            print(f"Erro crítico ao carregar imagem de fundo: {e}")
            # Carrega um fundo padrão em caso de erro
            self.fundo_label = ctk.CTkLabel(self, text="", fg_color="#1a1a1a")
            self.fundo_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.fundo_label.lower()

    def on_resize(self, event):
        """Método para lidar com o redimensionamento da janela e atualizar a imagem de fundo."""
        if self.imagem_pil_fundo and self.fundo_label:
            largura = self.winfo_width()
            altura = self.winfo_height()

            if largura > 0 and altura > 0:
                img_largura, img_altura = self.imagem_pil_fundo.size
                
                ratio = max(largura / img_largura, altura / img_altura)
                nova_largura = int(img_largura * ratio)
                nova_altura = int(img_altura * ratio)
                
                imagem_redimensionada = self.imagem_pil_fundo.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
                
                left = (nova_largura - largura) / 2
                top = (nova_altura - altura) / 2
                right = (nova_largura + largura) / 2
                bottom = (nova_altura + altura) / 2
                
                imagem_final = imagem_redimensionada.crop((left, top, right, bottom))
                
                self.tk_image_fundo = ctk.CTkImage(imagem_final, size=(largura, altura))
                self.fundo_label.configure(image=self.tk_image_fundo)
                self.fundo_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.fundo_label.lower()
                self._organizar_camadas_ui()

    def _organizar_camadas_ui(self):
        """Garante que os elementos da interface estejam por cima da imagem de fundo."""
        if hasattr(self, 'fundo_label'):
            self.fundo_label.lower()
        if hasattr(self, 'botoes_frame'):
            self.botoes_frame.lift()
        if hasattr(self, 'pesquisa_frame'):
            self.pesquisa_frame.lift()
        # O resultado_frame só é levantado se já estiver empacotado/visível
        if hasattr(self, 'resultado_frame') and self.resultado_frame.winfo_ismapped():
            self.resultado_frame.lift()
            self.resultado_frame.lift()  # Lift adicional para garantir que fique acima

        self.update_idletasks()



    def _inicializar_componentes_visuais(self):
        """Inicializa e empacota os componentes visuais da interface com verificações de dependências."""
        try:
            # Verifica se o customtkinter está instalado
            import customtkinter as ctk
            
            # Cria frame principal
            self.botoes_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.botoes_frame.pack(pady=10, padx=10, fill="x", side="top")

            # Lista de botões principais
            botoes = [
                {"text": "Trabalho", "command": self.on_trabalho_click},
                {"text": "Web", "command": self.on_web_click},
                {"text": "Música", "command": self.on_musica_click},
                {"text": "Redes", "command": self._abrir_janela_redes},
                {"text": "Vídeos", "command": self.on_videos_click},
                {"text": "Dashboard", "command": self.on_dashboard_click},
                {"text": "Sobre", "command": self.mostrar_sobre},
            ]
            
            # Cria botões dinamicamente
            for botao in botoes:
                btn = ctk.CTkButton(
                    self.botoes_frame, 
                    text=botao["text"], 
                    command=botao["command"], 
                    width=100, 
                    fg_color="transparent", 
                    border_width=0, 
                    hover_color="#333333"
                )
                btn.pack(side="left", padx=2)
                
            # Cria componentes de pesquisa imediatamente após os botões
            self._inicializar_componentes_pesquisa()
                
        except ImportError as e:
            print(f"Erro crítico: {e}")
            # Fallback básico se customtkinter não estiver disponível
            self.botoes_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
            self.botoes_frame.pack(fill="both", expand=True)
            ctk.CTkLabel(self.botoes_frame, text="Erro: Dependências não encontradas", text_color="red").pack()
            
    def _inicializar_componentes_pesquisa(self):
        """Inicializa os componentes de pesquisa de forma otimizada."""
        # Frame para a barra de pesquisa e botão Salvar
        self.pesquisa_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=1, border_color="white")
        self.pesquisa_frame.pack(side="top", fill="x", padx=10, pady=10)

        self.pesquisa_entry = ctk.CTkEntry(self.pesquisa_frame, fg_color="transparent", placeholder_text="Pesquisar na Wikipedia...")
        self.pesquisa_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.pesquisa_entry.bind('<Return>', self.pesquisar_wikipedia_interface)

        # Botão "Salvar"
        self.salvar_btn = ctk.CTkButton(self.pesquisa_frame, text="Salvar", command=self.on_salvar_click)
        self.salvar_btn.pack(side="right", padx=5, pady=5)

        # Frame para exibir resultados de pesquisa (INICIALMENTE INVISÍVEL)
        self.resultado_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", width=780, height=350)
        self.resultado_frame.pack_forget() # <-- ESSENCIAL: Oculta o frame no início

        self.resultado_label = ctk.CTkLabel(self.resultado_frame, text="", wraplength=740, justify="left", fg_color="transparent", text_color="white", font=("Segoe UI", 12))
        self.resultado_label.pack(fill="both", expand=True, padx=20, pady=20)
            
    def on_trabalho_click(self):
        """Ação para o botão Trabalho - abre uma janela com ferramentas de produtividade"""
        janela_trabalho = ctk.CTkToplevel(self)
        janela_trabalho.title("Ferramentas de Trabalho")
        janela_trabalho.geometry("400x300")
        janela_trabalho.transient(self)
        janela_trabalho.grab_set()
        
        frame = ctk.CTkFrame(janela_trabalho)
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkButton(frame, text="Abrir Word", 
                     command=lambda: os.startfile("winword.exe")).pack(pady=5, fill="x")
        ctk.CTkButton(frame, text="Abrir Excel", 
                     command=lambda: os.startfile("excel.exe")).pack(pady=5, fill="x")
        ctk.CTkButton(frame, text="Abrir PowerPoint", 
                     command=lambda: os.startfile("powerpnt.exe")).pack(pady=5, fill="x")
        ctk.CTkButton(frame, text="Abrir Bloco de Notas", 
                     command=lambda: os.startfile("notepad.exe")).pack(pady=5, fill="x")
        
        janela_trabalho.protocol("WM_DELETE_WINDOW", lambda: janela_trabalho.destroy())
        
    def mostrar_sobre(self):
        """Exibe informações sobre o aplicativo a partir do arquivo README.txt"""
        try:
            readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.txt")
            with open(readme_path, "r", encoding="utf-8") as file:
                conteudo = file.read()
                
            janela_sobre = ctk.CTkToplevel(self)
            janela_sobre.title("Sobre o Aplicativo")
            janela_sobre.geometry("800x600")
            janela_sobre.attributes('-topmost', True)
            janela_sobre.transient(self)
            janela_sobre.grab_set()
            
            # Frame principal com padding
            frame_principal = ctk.CTkFrame(janela_sobre)
            frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Frame rolável para o conteúdo
            frame = ctk.CTkScrollableFrame(frame_principal)
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Label com o texto formatado
            label = ctk.CTkLabel(frame, 
                                text=conteudo, 
                                justify="left",
                                wraplength=700,
                                font=("Arial", 14))
            label.pack(fill="both", expand=True, padx=20, pady=10)
            
            janela_sobre.protocol("WM_DELETE_WINDOW", lambda: janela_sobre.destroy())
            
        except Exception as e:
            print(f"Erro ao exibir informações: {e}")


    def pesquisar_wikipedia_interface(self, event=None):
        """Realiza pesquisa na Wikipedia e exibe os resultados na interface."""
        query = self.pesquisa_entry.get().strip()
        if not query:
            # Se a query estiver vazia, oculta o frame e exibe mensagem
            self._ocultar_resultado_busca()
            self.show_temporary_message("Por favor, digite algo para pesquisar.")
            return

        self.pesquisa_entry.delete(0, 'end')
        
        # Mostra o frame e a mensagem de "Buscando..."
        self._exibir_resultado_busca(query, "Buscando na Wikipedia...")
        
        # Executa a busca em thread separada
        try:
            threading.Thread(
                target=self._executar_busca_wikipedia,
                args=(query,),
                daemon=True
            ).start()
        except Exception as e:
            self._exibir_resultado_busca(query, f"Erro ao iniciar busca: {str(e)}")

    def _exibir_resultado_busca(self, query, resultado):
        """Atualiza o label de resultados e TORNA O FRAME VISÍVEL."""
        self.resultado_label.configure(text=f"Resultados para '{query}':\n\n{resultado}" if query else resultado, justify="left")
        
        # Se o frame não estiver mapeado (visível), empacota ele
        if not self.resultado_frame.winfo_ismapped():
            self.resultado_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.resultado_frame.lift() # Garante que ele esteja por cima
        self._organizar_camadas_ui() # Reorganiza as camadas após exibir o frame

    def _ocultar_resultado_busca(self):
        """Oculta o frame de resultados."""
        if self.resultado_frame.winfo_ismapped():
            self.resultado_frame.pack_forget()
        self.resultado_label.configure(text="") # Limpa o texto também

    def _executar_busca_wikipedia(self, query):
        """Executa a busca na Wikipedia em uma thread separada."""
        try:
            import wikipedia
            wikipedia.set_lang('pt')
            
            # Tenta obter o resumo da Wikipedia
            resultado = wikipedia.summary(query, sentences=10)
            
            # Tenta obter mais informações da página completa
            try:
                page = wikipedia.page(query)
                resultado += f"\n\nMais informações: {page.url}"
            except:
                pass
                
            self._exibir_resultado_busca(query, resultado)
            
        except wikipedia.exceptions.DisambiguationError as e:
            options = "\n- " + "\n- ".join(e.options[:5])
            self._exibir_resultado_busca(query, f"Múltiplos resultados encontrados para '{query}'. Opções:\n{options}")
            
        except wikipedia.exceptions.PageError:
            self._exibir_resultado_busca(query, f"Nenhum resultado encontrado para '{query}'.")
            
        except Exception as e:
            self._exibir_resultado_busca(query, f"Erro ao buscar na Wikipedia: {str(e)}")
            
        # Garante que o frame de resultados seja exibido
        self.resultado_frame.pack(fill="both", expand=True)

    def on_salvar_click(self):
        """Ação para o botão Salvar."""
        texto_para_salvar = self.resultado_label.cget("text")
        if texto_para_salvar and self.resultado_frame.winfo_ismapped():
            # Copia o texto para área de transferência
            pyperclip.copy(texto_para_salvar)
            
            # Criar nova janela para opções de salvamento
            janela_salvar = ctk.CTkToplevel(self)
            janela_salvar.title("Salvar Resultado")
            janela_salvar.geometry("300x150")
            janela_salvar.transient(self)
            janela_salvar.grab_set()

            frame_botoes = ctk.CTkFrame(janela_salvar)
            frame_botoes.pack(pady=20, padx=20, fill="both", expand=True)

            def salvar_word():
                try:
                    subprocess.Popen('"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Word 2016.lnk"', shell=True)
                    word = win32com.client.Dispatch("Word.Application")
                    doc = word.Documents.Add()
                    doc.Content.Text = texto_para_salvar
                    doc.SaveAs("Resultado_Wikipedia.docx")
                    doc.Close()
                    word.Quit()
                    self.show_temporary_message("Salvo no Word com sucesso!")
                except Exception as e:
                    self.show_temporary_message(f"Erro ao salvar no Word: {e}")
                finally:
                    janela_salvar.destroy()

            def salvar_bloco():
                try:
                    with open("Resultado_Wikipedia.txt", "w", encoding="utf-8") as f:
                        f.write(texto_para_salvar)
                    subprocess.Popen("notepad.exe Resultado_Wikipedia.txt", shell=True)
                    self.show_temporary_message("Salvo no Bloco de Notas!")
                except Exception as e:
                    self.show_temporary_message(f"Erro ao salvar: {e}")
                finally:
                    janela_salvar.destroy()

            ctk.CTkButton(frame_botoes, text="Salvar no Word", command=salvar_word).pack(pady=5, fill="x")
            ctk.CTkButton(frame_botoes, text="Salvar no Bloco de Notas", command=salvar_bloco).pack(pady=5, fill="x")

            janela_salvar.protocol("WM_DELETE_WINDOW", lambda: janela_salvar.destroy())
        else:
            self.show_temporary_message("Nenhum resultado visível para salvar.")

    def show_temporary_message(self, message):
        """Exibe uma mensagem temporária na janela."""
        msg_label = ctk.CTkLabel(self, text=message, text_color="yellow", fg_color="gray", corner_radius=5, padx=10, pady=5)
        msg_label.place(relx=0.5, rely=0.15, anchor="center")



    def on_musica_click(self):
        from media.MR import janela_pesquisa_musica
        janela_pesquisa_musica()
            
    def _abrir_janela_radios(self):
        """Abre a subjanela de rádios diretamente usando JanelaRadio."""
        from media.MR import JanelaRadio
        if hasattr(self, 'janela_radio') and self.janela_radio.winfo_exists():
            self.janela_radio.lift()
            return
        self.janela_radio = JanelaRadio()
        self.janela_radio.protocol("WM_DELETE_WINDOW", self._fechar_janela_radios)
        
        
    def _pesquisar_musica_youtube(self):
        """Abre o YouTube Music com a pesquisa digitada."""
        query = self.entry_musica.get().strip()
        if query:
            url = f"https://music.youtube.com/search?q={requests.utils.quote(query)}"
            webbrowser.open(url, new=2)
            self.entry_musica.delete(0, 'end')

    def _fechar_janela_radios(self):
        """Para a reprodução da rádio e fecha a janela."""
        try:
            # Para a reprodução usando o player VLC se estiver ativo
            if 'player' in globals() and player:
                player.stop()
                player.release()
                
            # Para a reprodução usando Windows Media Player se estiver ativo
            if 'wmp' in globals() and wmp:
                wmp.controls.stop()
        except Exception as e:
            print(f"Erro ao parar a reprodução: {e}")
        finally:
            if hasattr(self, 'janela_radio') and self.janela_radio.winfo_exists():
                self.janela_radio.destroy()



    def _abrir_janela_redes(self):
        from redes_sociais import JanelaRedes
        if self.janela_redes is None or not self.janela_redes.winfo_exists():
            self.janela_redes = JanelaRedes()
            self.janela_redes.protocol("WM_DELETE_WINDOW", lambda: self._on_toplevel_close(self.janela_redes, "janela_redes"))
            self.janela_redes.attributes('-topmost', True)
            self.janela_redes.mainloop()
        else:
            self.janela_redes.focus()
            
            
    def on_videos_click(self):
        if not self.videos_window or not self.videos_window.winfo_exists():
            self.videos_window = App()
            self.videos_window.protocol("WM_DELETE_WINDOW", lambda: self._on_toplevel_close(self.videos_window, "videos_window"))
            self.videos_window.mainloop()

    def _on_toplevel_close(self, window, attr_name=None):
        window.destroy()
        if attr_name and hasattr(self, attr_name):
            setattr(self, attr_name, None)

    def on_web_click(self):
        janela_busca = ctk.CTkToplevel(self)
        janela_busca.title("Busca Web")
        janela_busca.geometry("500x300")
        janela_busca.transient(self)
        janela_busca.grab_set()

        frame_principal = ctk.CTkFrame(janela_busca)
        frame_principal.pack(pady=20, padx=20, fill="both", expand=True)

        self.entry_busca = ctk.CTkEntry(frame_principal, placeholder_text="Digite sua busca...")
        self.entry_busca.pack(pady=10, fill="x")
        self.entry_busca.bind('<Return>', lambda e: self._executar_busca_web_janela())

        frame_checkboxes = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_checkboxes.pack(pady=10, fill="x")
        
        self.check_imagens = ctk.CTkCheckBox(frame_checkboxes, text="Imagens")
        self.check_imagens.pack(side="left", padx=10)
        
        self.check_livros = ctk.CTkCheckBox(frame_checkboxes, text="Livros")
        self.check_livros.pack(side="left", padx=10)
        
        # Frame para pesquisa de CEP/endereço
        frame_maps = ctk.CTkFrame(frame_principal)
        frame_maps.pack(pady=10, fill="x")
        
        self.entry_maps = ctk.CTkEntry(frame_maps, placeholder_text="Digite CEP ou endereço")
        self.entry_maps.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_maps.bind('<Return>', lambda e: self._abrir_maps_com_endereco())

        self.btn_mapas = ctk.CTkButton(frame_maps, text="Abrir no Maps", command=self._abrir_maps_com_endereco)
        self.btn_mapas.pack(side="right", padx=5)
        
        janela_busca.protocol("WM_DELETE_WINDOW", lambda: self._on_toplevel_close(janela_busca))

    def _abrir_maps_com_endereco(self):
        endereco = self.entry_maps.get().strip()
        if endereco:
            url_maps = f"https://www.google.com/maps/search/{endereco.replace(' ', '+')}"
            webbrowser.open(url_maps)

    def on_dashboard_click(self):
        if abrir_dashboard_streamlit:
            abrir_dashboard_streamlit()

    def _executar_busca_web_janela(self):
        busca = self.entry_busca.get().strip()
        if busca:
            base_url = "https://www.google.com/search?q="
            if self.check_imagens.get():
                base_url = "https://www.google.com/search?tbm=isch&q="
            elif self.check_livros.get():
                base_url = "https://www.google.com/search?tbm=bks&q="
            
            url_busca = base_url + busca.replace(' ', '+')
            webbrowser.open(url_busca)

if __name__ == "__main__":
    app = JanelaPrincipal()
    app.mainloop()