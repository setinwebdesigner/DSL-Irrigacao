import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from irrigation_dsl import executar_sistema_irrigacao
import sys
from io import StringIO
from mqtt_handler import MQTTHandler
import json

class IrrigationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Irrigação DSL com MQTT")
        self.root.geometry("1000x800")
        
        # Inicializar MQTT
        self.mqtt_handler = MQTTHandler()
        self.registrar_callbacks_mqtt()
        
        # Configurar o estilo
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        
        # Criar o layout principal
        self.create_widgets()
        
        # Redirecionar a saída padrão para nossa área de texto
        self.original_stdout = sys.stdout
        self.output_buffer = StringIO()
        sys.stdout = self.output_buffer

    def registrar_callbacks_mqtt(self):
        """Registra os callbacks para os tópicos MQTT"""
        self.mqtt_handler.registrar_callback("umidade", self.atualizar_umidade)
        self.mqtt_handler.registrar_callback("temperatura", self.atualizar_temperatura)
        self.mqtt_handler.registrar_callback("bomba", self.atualizar_bomba)

    def atualizar_umidade(self, dados):
        """Callback para atualizar dados de umidade"""
        self.umidade_label.config(text=f"Umidade: {dados['valor']}{dados['unidade']}")
        self.output_text.insert(tk.END, f"Umidade atualizada: {dados}\n")
        self.output_text.see(tk.END)
        
        # Aplicar regras automaticamente
        if dados['valor'] < 30:
            self.mqtt_handler.client.publish("bomba", json.dumps({"bomba": "ligada"}))
            self.output_text.insert(tk.END, "⚠️ Umidade baixa -> Bomba LIGADA\n")
        else:
            self.mqtt_handler.client.publish("bomba", json.dumps({"bomba": "desligada"}))
            self.output_text.insert(tk.END, "⚠️ Umidade adequada -> Bomba DESLIGADA\n")
        self.output_text.see(tk.END)

    def atualizar_temperatura(self, dados):
        """Callback para atualizar dados de temperatura"""
        self.temperatura_label.config(text=f"Temperatura: {dados['valor']}{dados['unidade']}")
        self.output_text.insert(tk.END, f"Temperatura atualizada: {dados}\n")
        self.output_text.see(tk.END)
        
        # Aplicar regras automaticamente
        if dados['valor'] > 35:
            self.mqtt_handler.client.publish("ventilador", json.dumps({"ventilador": "ligado"}))
            self.output_text.insert(tk.END, "⚠️ Temperatura alta -> Ventilador LIGADO\n")
        else:
            self.mqtt_handler.client.publish("ventilador", json.dumps({"ventilador": "desligado"}))
            self.output_text.insert(tk.END, "⚠️ Temperatura adequada -> Ventilador DESLIGADO\n")
        self.output_text.see(tk.END)

    def atualizar_bomba(self, dados):
        """Callback para atualizar estado da bomba"""
        self.bomba_label.config(text=f"Bomba: {dados['estado']}")
        self.output_text.insert(tk.END, f"Estado da bomba atualizado: {dados}\n")
        self.output_text.see(tk.END)

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame para status MQTT
        status_frame = ttk.LabelFrame(main_frame, text="Status dos Sensores", padding="5")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.umidade_label = ttk.Label(status_frame, text="Umidade: --")
        self.umidade_label.grid(row=0, column=0, padx=5)
        
        self.temperatura_label = ttk.Label(status_frame, text="Temperatura: --")
        self.temperatura_label.grid(row=0, column=1, padx=5)
        
        self.bomba_label = ttk.Label(status_frame, text="Bomba: --")
        self.bomba_label.grid(row=0, column=2, padx=5)
        
        # Área de edição do programa
        ttk.Label(main_frame, text="Digite seu programa de irrigação:").grid(row=1, column=0, sticky=tk.W)
        
        self.program_text = scrolledtext.ScrolledText(main_frame, width=70, height=15)
        self.program_text.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Executar", command=self.run_program).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar Tudo", command=self.clear_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar Programa", command=self.clear_program).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar Saída", command=self.clear_output_only).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exemplo", command=self.load_example).pack(side=tk.LEFT, padx=5)
        
        # Área de saída
        ttk.Label(main_frame, text="Saída do programa:").grid(row=4, column=0, sticky=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(main_frame, width=70, height=15)
        self.output_text.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Configurar cores e fontes
        self.program_text.configure(font=("Courier", 10))
        self.output_text.configure(font=("Courier", 10))
        
        # Carregar programa de exemplo
        self.load_example()

    def run_program(self):
        # Limpar saída anterior
        self.output_text.delete(1.0, tk.END)
        
        # Obter o programa
        programa = self.program_text.get(1.0, tk.END).strip()
        
        # Validação básica
        if not programa:
            messagebox.showerror("Erro", "O programa está vazio!")
            return
            
        # Verificar estrutura básica
        linhas = programa.split('\n')
        encontrou_sensor = False
        encontrou_regra = False
        
        for i, linha in enumerate(linhas, 1):
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue
                
            # Verificar declaração de sensor
            if linha.startswith('INSERIR SENSOR'):
                encontrou_sensor = True
            # Verificar regras
            elif linha.startswith('SE SENSOR'):
                if not encontrou_sensor:
                    messagebox.showerror("Erro de Sintaxe", 
                        "Erro na linha {}: Você deve declarar os sensores (INSERIR SENSOR) antes de usar regras SE!\n\n"
                        "Exemplo de estrutura correta:\n"
                        "INSERIR SENSOR \"Nome do Sensor\" ID 1\n"
                        "SE SENSOR 1 < 30 ENTAO LIGAR \"Dispositivo\"".format(i))
                    return
                encontrou_regra = True
            # Verificar se a linha segue algum padrão conhecido
            elif not (linha.startswith('ESPERAR') or linha.startswith('INSERIR') or linha.startswith('SE')):
                messagebox.showerror("Erro de Sintaxe", 
                    "Erro na linha {}: Comando não reconhecido: '{}'\n\n"
                    "Comandos válidos:\n"
                    "- INSERIR SENSOR \"Nome\" ID número\n"
                    "- SE SENSOR id operador valor ENTAO LIGAR|DESLIGAR \"Dispositivo\"\n"
                    "- ESPERAR segundos".format(i, linha))
                return
        
        if not encontrou_sensor:
            messagebox.showerror("Erro de Estrutura", 
                "O programa deve conter pelo menos uma declaração de sensor (INSERIR SENSOR)!\n\n"
                "Exemplo:\n"
                "INSERIR SENSOR \"Umidade Solo\" ID 1")
            return
            
        if not encontrou_regra:
            messagebox.showerror("Erro de Estrutura", 
                "O programa deve conter pelo menos uma regra (SE)!\n\n"
                "Exemplo:\n"
                "SE SENSOR 1 < 30 ENTAO LIGAR \"Bomba\"")
            return
        
        try:
            # Executar o programa
            executar_sistema_irrigacao(programa)
            
            # Atualizar a área de saída
            output = self.output_buffer.getvalue()
            if "Erro" in output or "erro" in output:
                self.output_text.insert(tk.END, "❌ ERROS ENCONTRADOS:\n" + output)
            else:
                self.output_text.insert(tk.END, output)
            
            # Limpar o buffer
            self.output_buffer.truncate(0)
            self.output_buffer.seek(0)
            
        except Exception as e:
            erro = str(e)
            if "não foi declarado" in erro:
                messagebox.showerror("Erro", 
                    "Erro de Sensor não Declarado!\n\n"
                    "Lembre-se de declarar todos os sensores antes de usá-los:\n"
                    "INSERIR SENSOR \"Nome\" ID número")
            else:
                messagebox.showerror("Erro", 
                    "Erro ao executar o programa:\n{}\n\n"
                    "Verifique se seu programa segue a estrutura correta:\n"
                    "1. Declare os sensores (INSERIR SENSOR)\n"
                    "2. Defina as regras (SE)\n"
                    "3. Use ESPERAR para esperas".format(erro))

    def clear_program(self):
        """Limpa apenas a área do programa"""
        self.program_text.delete(1.0, tk.END)

    def clear_output_only(self):
        """Limpa apenas a área de saída"""
        self.output_text.delete(1.0, tk.END)
        self.output_buffer.truncate(0)
        self.output_buffer.seek(0)

    def clear_output(self):
        """Limpa todas as áreas"""
        # Limpar área do programa
        self.program_text.delete(1.0, tk.END)
        # Limpar área de saída
        self.output_text.delete(1.0, tk.END)
        # Limpar buffer
        self.output_buffer.truncate(0)
        self.output_buffer.seek(0)

    def load_example(self):
        exemplo = '''# Programa de irrigação
INSERIR SENSOR "Umidade Solo 1" ID 1
INSERIR SENSOR "Umidade Solo 2" ID 2
INSERIR SENSOR "Temperatura" ID 3

# Regras para a primeira área
SE SENSOR 1 < 30 ENTAO LIGAR "Bomba 1"
SE SENSOR 1 >= 30 ENTAO DESLIGAR "Bomba 1"

# Regras para a segunda área
SE SENSOR 2 < 25 ENTAO LIGAR "Bomba 2"
SE SENSOR 2 >= 25 ENTAO DESLIGAR "Bomba 2"

# Regras para controle de temperatura
SE SENSOR 3 > 35 ENTAO LIGAR "Ventilador"
SE SENSOR 3 <= 35 ENTAO DESLIGAR "Ventilador"

ESPERAR 5'''
        
        self.program_text.delete(1.0, tk.END)
        self.program_text.insert(1.0, exemplo)

    def __del__(self):
        # Restaurar a saída padrão
        sys.stdout = self.original_stdout
        # Desconectar do MQTT
        self.mqtt_handler.desconectar()

def main():
    root = tk.Tk()
    app = IrrigationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 