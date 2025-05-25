import subprocess
import os
import sys

def abrir_dashboard_streamlit():
    try:
        # Obtém o caminho absoluto do diretório do script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_dashboard = os.path.join(base_dir, "auto_dashboard.py")
        
        if not os.path.exists(caminho_dashboard):
            print(f"Erro: arquivo {caminho_dashboard} não encontrado")
            return
            
        # Usa o caminho completo do Python do ambiente atual
        python_exe = sys.executable
        comando = [python_exe, "-m", "streamlit", "run", caminho_dashboard]
        
        # Verifica se já existe uma instância rodando
        try:
            # Tenta conectar na porta padrão do Streamlit
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("localhost", 8501))
            sock.close()
            
            if result == 0:
                # Porta em uso, Streamlit já está rodando
                import webbrowser
                webbrowser.open("http://localhost:8501")
                return
        except:
            pass  # Ignora erros na verificação da porta
            
        # Inicia nova instância do Streamlit
        subprocess.Popen(comando, creationflags=subprocess.CREATE_NO_WINDOW)
        
    except Exception as e:
        print(f"Erro ao iniciar o Streamlit: {e}")

# Use diretamente se quiser rodar como script
if __name__ == "__main__":
    abrir_dashboard_streamlit()
