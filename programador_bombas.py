import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

class ProgramadorBombas:
    def __init__(self, root):
        self.root = root
        self.root.title("Programador de Bombas")
        self.root.geometry("800x600")
        
        # Configuração MQTT
        self.client = mqtt.Client()
        self.broker = "localhost"  # Altere para o IP do seu broker
        self.port = 1883
        self.conectar_mqtt()
        
        # Variáveis de controle
        self.programas = []
        self.executando = False
        
        self.criar_interface()
        
    def conectar_mqtt(self):
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
            print("Conectado ao broker MQTT!")
        except Exception as e:
            print(f"Erro ao conectar ao broker MQTT: {e}")
    
    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Frame de configuração das bombas
        config_frame = ttk.LabelFrame(main_frame, text="Configuração de Bombas", padding="5")
        config_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Seleção da bomba
        ttk.Label(config_frame, text="Bomba:").grid(row=0, column=0, padx=5)
        self.bomba_var = tk.StringVar(value="1")
        bomba_combo = ttk.Combobox(config_frame, textvariable=self.bomba_var, values=["1", "2", "3"], width=5)
        bomba_combo.grid(row=0, column=1, padx=5)
        
        # Condição
        ttk.Label(config_frame, text="Condição:").grid(row=0, column=2, padx=5)
        self.condicao_var = tk.StringVar(value="timer")
        condicao_combo = ttk.Combobox(config_frame, textvariable=self.condicao_var, 
                                    values=["timer", "horário"], width=10)
        condicao_combo.grid(row=0, column=3, padx=5)
        
        # Valor
        ttk.Label(config_frame, text="Valor:").grid(row=0, column=4, padx=5)
        self.valor_entry = ttk.Entry(config_frame, width=10)
        self.valor_entry.grid(row=0, column=5, padx=5)
        
        # Ação
        ttk.Label(config_frame, text="Ação:").grid(row=0, column=6, padx=5)
        self.acao_var = tk.StringVar(value="ligar")
        acao_combo = ttk.Combobox(config_frame, textvariable=self.acao_var, 
                                 values=["ligar", "desligar"], width=10)
        acao_combo.grid(row=0, column=7, padx=5)
        
        # Botão adicionar
        ttk.Button(config_frame, text="Adicionar", command=self.adicionar_programa).grid(row=0, column=8, padx=5)
        
        # Lista de programas
        ttk.Label(main_frame, text="Programas configurados:").grid(row=1, column=0, sticky="w", pady=(10,0))
        self.lista_programas = scrolledtext.ScrolledText(main_frame, width=80, height=15)
        self.lista_programas.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Frame de controle
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Botões de controle
        ttk.Button(control_frame, text="Iniciar", command=self.iniciar_execucao).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Parar", command=self.parar_execucao).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Limpar", command=self.limpar_programas).pack(side=tk.LEFT, padx=5)
        
        # Log de execução
        ttk.Label(main_frame, text="Log de execução:").grid(row=4, column=0, sticky="w")
        self.log_text = scrolledtext.ScrolledText(main_frame, width=80, height=10)
        self.log_text.grid(row=5, column=0, columnspan=2, pady=5)
    
    def adicionar_programa(self):
        bomba = self.bomba_var.get()
        condicao = self.condicao_var.get()
        valor = self.valor_entry.get()
        acao = self.acao_var.get()
        
        # Validação
        if not valor:
            messagebox.showerror("Erro", "O valor não pode estar vazio!")
            return
        
        if condicao == "timer":
            try:
                segundos = int(valor)
                if segundos <= 0:
                    raise ValueError
                valor_formatado = f"{segundos} segundos"
            except ValueError:
                messagebox.showerror("Erro", "Para timer, o valor deve ser um número inteiro positivo!")
                return
        elif condicao == "horário":
            try:
                # Validar formato HH:MM
                datetime.strptime(valor, "%H:%M")
                valor_formatado = valor
            except ValueError:
                messagebox.showerror("Erro", "Para horário, use o formato HH:MM (exemplo: 14:30)!")
                return
        
        programa = {
            "bomba": bomba,
            "condicao": condicao,
            "valor": valor,
            "valor_formatado": valor_formatado,
            "acao": acao
        }
        
        self.programas.append(programa)
        self.atualizar_lista_programas()
        self.valor_entry.delete(0, tk.END)
    
    def atualizar_lista_programas(self):
        self.lista_programas.delete(1.0, tk.END)
        for i, prog in enumerate(self.programas, 1):
            self.lista_programas.insert(tk.END, 
                f"{i}. Bomba {prog['bomba']}: {prog['acao'].upper()} quando {prog['condicao']} = {prog['valor_formatado']}\n")
    
    def enviar_comando_bomba(self, bomba, acao):
        comando = "01" if acao == "ligar" else "00"
        if bomba == "2":
            comando = "02" if acao == "ligar" else "00"
        elif bomba == "3":
            comando = "03" if acao == "ligar" else "00"
        
        topico = f"bomba{bomba}"
        self.client.publish(topico, comando)
        self.log(f"Enviado comando {comando} para {topico}")
    
    def log(self, mensagem):
        agora = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{agora}] {mensagem}\n")
        self.log_text.see(tk.END)
    
    def executar_programas(self):
        while self.executando:
            hora_atual = datetime.now().strftime("%H:%M")
            
            for programa in self.programas:
                if programa["condicao"] == "horário" and programa["valor"] == hora_atual:
                    self.enviar_comando_bomba(programa["bomba"], programa["acao"])
                elif programa["condicao"] == "timer":
                    segundos = int(programa["valor"])
                    self.enviar_comando_bomba(programa["bomba"], programa["acao"])
                    self.log(f"Aguardando {segundos} segundos...")
                    time.sleep(segundos)
                    # Inverte a ação após o timer
                    acao_inversa = "desligar" if programa["acao"] == "ligar" else "ligar"
                    self.enviar_comando_bomba(programa["bomba"], acao_inversa)
            
            time.sleep(1)  # Verifica a cada segundo
    
    def iniciar_execucao(self):
        if not self.programas:
            messagebox.showwarning("Aviso", "Não há programas configurados!")
            return
        
        if not self.executando:
            self.executando = True
            self.log("Iniciando execução dos programas...")
            import threading
            self.thread_execucao = threading.Thread(target=self.executar_programas)
            self.thread_execucao.daemon = True
            self.thread_execucao.start()
    
    def parar_execucao(self):
        if self.executando:
            self.executando = False
            self.log("Parando execução dos programas...")
            # Desliga todas as bombas
            for bomba in ["1", "2", "3"]:
                self.enviar_comando_bomba(bomba, "desligar")
    
    def limpar_programas(self):
        self.programas = []
        self.atualizar_lista_programas()
        self.log("Lista de programas limpa!")
    
    def __del__(self):
        self.parar_execucao()
        self.client.loop_stop()
        self.client.disconnect()

def main():
    root = tk.Tk()
    app = ProgramadorBombas(root)
    root.mainloop()

if __name__ == "__main__":
    main() 