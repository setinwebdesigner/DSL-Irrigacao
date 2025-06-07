import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

class SistemaIrrigacao:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Irrigação Integrado")
        self.root.geometry("1200x600")
        
        # Valores dos sensores
        self.umidade1 = 0
        self.umidade2 = 0
        self.temperatura = 0
        
        # Thresholds (valores padrão)
        self.threshold_umidade1 = 30
        self.threshold_umidade2 = 25
        self.threshold_temperatura = 35
        
        # Configuração MQTT
        self.client = mqtt.Client()
        self.broker = "localhost"  # Altere para o IP do seu broker
        self.port = 1883
        
        # Configurar callbacks MQTT
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Conectar ao broker
        self.conectar_mqtt()
        
        # Criar interface
        self.criar_interface()
        
    def conectar_mqtt(self):
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
            print("Conectado ao broker MQTT!")
        except Exception as e:
            print(f"Erro ao conectar ao broker MQTT: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao broker MQTT!")
            # Inscrever nos tópicos
            self.client.subscribe("umidade")
            self.client.subscribe("umidade2")
            self.client.subscribe("temperatura")
        else:
            print(f"Falha na conexão com o broker MQTT. Código: {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            # Decodificar a mensagem JSON
            payload = msg.payload.decode()
            topic = msg.topic
            dados = json.loads(payload)
            
            # Extrair o valor do JSON
            if topic == "umidade":
                valor = float(dados["umidade"])
                self.umidade1 = valor
                self.umidade1_label.config(text=f"Umidade Solo 1: {valor:.1f}%")
                self.verificar_condicao_bomba1()
            
            elif topic == "umidade2":
                valor = float(dados["umidade"])
                self.umidade2 = valor
                self.umidade2_label.config(text=f"Umidade Solo 2: {valor:.1f}%")
                self.verificar_condicao_bomba2()
            
            elif topic == "temperatura":
                valor = float(dados["temperatura"])
                self.temperatura = valor
                self.temperatura_label.config(text=f"Temperatura: {valor:.1f}°C")
                self.verificar_condicao_bomba3()
            
            # Registrar no log
            self.log(f"Recebido {topic}: {valor:.1f}")
            
        except Exception as e:
            print(f"Erro ao processar mensagem do tópico {topic}: {e}")
            print(f"Payload recebido: {payload}")
    
    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill='both')
        
        # Status dos sensores
        sensor_frame = ttk.LabelFrame(main_frame, text="Status dos Sensores", padding="5")
        sensor_frame.pack(fill='x', padx=5, pady=5)
        
        self.umidade1_label = ttk.Label(sensor_frame, text="Umidade Solo 1: --")
        self.umidade1_label.pack(side='left', padx=10)
        
        self.umidade2_label = ttk.Label(sensor_frame, text="Umidade Solo 2: --")
        self.umidade2_label.pack(side='left', padx=10)
        
        self.temperatura_label = ttk.Label(sensor_frame, text="Temperatura: --")
        self.temperatura_label.pack(side='left', padx=10)
        
        # Frame de configuração das regras
        config_frame = ttk.LabelFrame(main_frame, text="Configuração das Regras", padding="5")
        config_frame.pack(fill='x', padx=5, pady=5)
        
        # Umidade 1
        ttk.Label(config_frame, text="Umidade Solo 1 mínima (%):").pack(side='left', padx=5)
        self.umidade1_entry = ttk.Entry(config_frame, width=5)
        self.umidade1_entry.insert(0, str(self.threshold_umidade1))
        self.umidade1_entry.pack(side='left', padx=5)
        
        # Umidade 2
        ttk.Label(config_frame, text="Umidade Solo 2 mínima (%):").pack(side='left', padx=5)
        self.umidade2_entry = ttk.Entry(config_frame, width=5)
        self.umidade2_entry.insert(0, str(self.threshold_umidade2))
        self.umidade2_entry.pack(side='left', padx=5)
        
        # Temperatura
        ttk.Label(config_frame, text="Temperatura máxima (°C):").pack(side='left', padx=5)
        self.temperatura_entry = ttk.Entry(config_frame, width=5)
        self.temperatura_entry.insert(0, str(self.threshold_temperatura))
        self.temperatura_entry.pack(side='left', padx=5)
        
        # Botão para atualizar regras
        ttk.Button(config_frame, text="Atualizar Regras", command=self.atualizar_regras).pack(side='left', padx=20)
        
        # Status das bombas
        bomba_frame = ttk.LabelFrame(main_frame, text="Status das Bombas", padding="5")
        bomba_frame.pack(fill='x', padx=5, pady=5)
        
        self.bomba1_label = ttk.Label(bomba_frame, text="Bomba 1: Desligada")
        self.bomba1_label.pack(side='left', padx=10)
        
        self.bomba2_label = ttk.Label(bomba_frame, text="Bomba 2: Desligada")
        self.bomba2_label.pack(side='left', padx=10)
        
        self.bomba3_label = ttk.Label(bomba_frame, text="Bomba 3: Desligada")
        self.bomba3_label.pack(side='left', padx=10)
        
        # Regras atuais
        regras_frame = ttk.LabelFrame(main_frame, text="Regras Atuais", padding="5")
        regras_frame.pack(fill='x', padx=5, pady=5)
        
        self.regra1_label = ttk.Label(regras_frame, text=f"• Se Umidade Solo 1 < {self.threshold_umidade1}% -> Liga Bomba 1")
        self.regra1_label.pack(anchor='w')
        
        self.regra2_label = ttk.Label(regras_frame, text=f"• Se Umidade Solo 2 < {self.threshold_umidade2}% -> Liga Bomba 2")
        self.regra2_label.pack(anchor='w')
        
        self.regra3_label = ttk.Label(regras_frame, text=f"• Se Temperatura > {self.threshold_temperatura}°C -> Liga Bomba 3")
        self.regra3_label.pack(anchor='w')
        
        # Log de eventos
        log_frame = ttk.LabelFrame(main_frame, text="Log de Eventos", padding="5")
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=70, height=15)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def log(self, mensagem):
        agora = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{agora}] {mensagem}\n")
        self.log_text.see(tk.END)
    
    def atualizar_regras(self):
        """Atualiza os thresholds com os valores inseridos pelo usuário"""
        try:
            # Validar e atualizar Umidade 1
            novo_u1 = float(self.umidade1_entry.get())
            if 0 <= novo_u1 <= 100:
                self.threshold_umidade1 = novo_u1
            else:
                raise ValueError("Umidade deve estar entre 0 e 100%")
            
            # Validar e atualizar Umidade 2
            novo_u2 = float(self.umidade2_entry.get())
            if 0 <= novo_u2 <= 100:
                self.threshold_umidade2 = novo_u2
            else:
                raise ValueError("Umidade deve estar entre 0 e 100%")
            
            # Validar e atualizar Temperatura
            novo_t = float(self.temperatura_entry.get())
            if 0 <= novo_t <= 60:
                self.threshold_temperatura = novo_t
            else:
                raise ValueError("Temperatura deve estar entre 0 e 60°C")
            
            # Atualizar labels das regras
            self.regra1_label.config(text=f"• Se Umidade Solo 1 < {self.threshold_umidade1}% -> Liga Bomba 1")
            self.regra2_label.config(text=f"• Se Umidade Solo 2 < {self.threshold_umidade2}% -> Liga Bomba 2")
            self.regra3_label.config(text=f"• Se Temperatura > {self.threshold_temperatura}°C -> Liga Bomba 3")
            
            # Log da atualização
            self.log(f"✅ Regras atualizadas com sucesso!")
            self.log(f"   Umidade 1: {self.threshold_umidade1}%")
            self.log(f"   Umidade 2: {self.threshold_umidade2}%")
            self.log(f"   Temperatura: {self.threshold_temperatura}°C")
            
            # Verificar condições atuais com as novas regras
            self.verificar_condicao_bomba1()
            self.verificar_condicao_bomba2()
            self.verificar_condicao_bomba3()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar regras: {str(e)}")
    
    def verificar_condicao_bomba1(self):
        if self.umidade1 < self.threshold_umidade1:
            self.enviar_comando_bomba("1", "ligar")
            self.log(f"⚠️ Umidade Solo 1 baixa ({self.umidade1:.1f}%) -> Ligando Bomba 1")
        else:
            self.enviar_comando_bomba("1", "desligar")
            self.log(f"✅ Umidade Solo 1 ok ({self.umidade1:.1f}%) -> Desligando Bomba 1")
    
    def verificar_condicao_bomba2(self):
        if self.umidade2 < self.threshold_umidade2:
            self.enviar_comando_bomba("2", "ligar")
            self.log(f"⚠️ Umidade Solo 2 baixa ({self.umidade2:.1f}%) -> Ligando Bomba 2")
        else:
            self.enviar_comando_bomba("2", "desligar")
            self.log(f"✅ Umidade Solo 2 ok ({self.umidade2:.1f}%) -> Desligando Bomba 2")
    
    def verificar_condicao_bomba3(self):
        if self.temperatura > self.threshold_temperatura:
            self.enviar_comando_bomba("3", "ligar")
            self.log(f"⚠️ Temperatura alta ({self.temperatura:.1f}°C) -> Ligando Bomba 3")
        else:
            self.enviar_comando_bomba("3", "desligar")
            self.log(f"✅ Temperatura ok ({self.temperatura:.1f}°C) -> Desligando Bomba 3")
    
    def enviar_comando_bomba(self, bomba, acao):
        comando = "01" if acao == "ligar" else "00"
        if bomba == "2":
            comando = "02" if acao == "ligar" else "00"
        elif bomba == "3":
            comando = "03" if acao == "ligar" else "00"
        
        topico = f"bomba{bomba}"
        self.client.publish(topico, comando)
        
        # Atualizar label da bomba
        label = getattr(self, f"bomba{bomba}_label")
        estado = "Ligada" if acao == "ligar" else "Desligada"
        label.config(text=f"Bomba {bomba}: {estado}")
    
    def __del__(self):
        self.client.loop_stop()
        self.client.disconnect()

def main():
    root = tk.Tk()
    app = SistemaIrrigacao(root)
    root.mainloop()

if __name__ == "__main__":
    main() 