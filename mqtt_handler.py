import paho.mqtt.client as mqtt
import json
from typing import Callable, Dict
import time

class MQTTHandler:
    def __init__(self, broker="localhost", port=1883):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.callbacks: Dict[str, Callable] = {}
        
        # Configurar callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Conectar ao broker
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
        except Exception as e:
            print(f"Erro ao conectar ao broker MQTT: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao broker MQTT!")
            # Inscrever nos tópicos
            self.client.subscribe("umidade")
            self.client.subscribe("temperatura")
            self.client.subscribe("bomba1")
            self.client.subscribe("bomba2")
            self.client.subscribe("bomba3")
        else:
            print(f"Falha na conexão com o broker MQTT. Código: {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            # Formatar os dados de acordo com o tópico
            if topic == "umidade":
                if isinstance(payload, dict) and "umidade" in payload:
                    payload = {"valor": payload["umidade"], "unidade": "%"}
                else:
                    print(f"Formato inválido para umidade. Use: {{'umidade': valor}}")
                    return
            
            elif topic == "temperatura":
                if isinstance(payload, dict) and "temperatura" in payload:
                    payload = {"valor": payload["temperatura"], "unidade": "C"}
                else:
                    print(f"Formato inválido para temperatura. Use: {{'temperatura': valor}}")
                    return
            
            elif topic in ["bomba1", "bomba2", "bomba3"]:
                if isinstance(payload, dict) and "comando" in payload:
                    comando = payload["comando"]
                    if comando in ["01", "02", "03", "00"]:
                        estado = "ligada" if comando != "00" else "desligada"
                        payload = {"estado": estado, "bomba": topic}
                    else:
                        print(f"Comando inválido para {topic}. Use: 01, 02, 03 ou 00")
                        return
                else:
                    print(f"Formato inválido para {topic}. Use: {{'comando': '01'}} ou {{'comando': '00'}}")
                    return
            
            if topic in self.callbacks:
                self.callbacks[topic](payload)
                
        except json.JSONDecodeError:
            print(f"Erro ao decodificar mensagem: {msg.payload}")
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
    
    def registrar_callback(self, topico: str, callback: Callable):
        """Registra uma função de callback para um tópico específico"""
        self.callbacks[topico] = callback
    
    def publicar(self, topico: str, dados: dict):
        """Publica dados em um tópico específico"""
        try:
            payload = json.dumps(dados)
            self.client.publish(topico, payload)
        except Exception as e:
            print(f"Erro ao publicar mensagem: {e}")
    
    def desconectar(self):
        """Desconecta do broker MQTT"""
        self.client.loop_stop()
        self.client.disconnect()

# Exemplo de uso
if __name__ == "__main__":
    def callback_umidade(dados):
        print(f"Umidade recebida: {dados}")
    
    def callback_temperatura(dados):
        print(f"Temperatura recebida: {dados}")
    
    def callback_bomba1(dados):
        print(f"Estado da bomba 1: {dados}")
    
    def callback_bomba2(dados):
        print(f"Estado da bomba 2: {dados}")
    
    def callback_bomba3(dados):
        print(f"Estado da bomba 3: {dados}")
    
    def callback_umidade_solo2(dados):
        print(f"Umidade Solo 2 recebida: {dados}")
    
    mqtt_handler = MQTTHandler()
    
    # Registrar callbacks
    mqtt_handler.registrar_callback("umidade", callback_umidade)
    mqtt_handler.registrar_callback("temperatura", callback_temperatura)
    mqtt_handler.registrar_callback("bomba1", callback_bomba1)
    mqtt_handler.registrar_callback("bomba2", callback_bomba2)
    mqtt_handler.registrar_callback("bomba3", callback_bomba3)
    mqtt_handler.registrar_callback("umidade_solo2", callback_umidade_solo2)
    
    # Exemplo de publicação
    try:
        while True:
            # Exemplos de diferentes formatos de mensagem
            mqtt_handler.publicar("umidade", {"valor": 65, "unidade": "%"})
            mqtt_handler.publicar("temperatura", {"valor": 25, "unidade": "C"})
            
            # Exemplos de comandos para as bombas (agora como strings simples)
            mqtt_handler.publicar("bomba1", "01")  # Ligar bomba 1
            mqtt_handler.publicar("bomba2", "02")  # Ligar bomba 2
            mqtt_handler.publicar("bomba3", "03")  # Ligar bomba 3
            mqtt_handler.publicar("bomba1", "00")  # Desligar bomba 1
            
            time.sleep(5)
    except KeyboardInterrupt:
        mqtt_handler.desconectar()

def atualizar_umidade(self, dados):
    """Callback para atualizar dados de umidade"""
    self.umidade_label.config(text=f"Umidade: {dados['valor']}{dados['unidade']}")
    self.output_text.insert(tk.END, f"Umidade atualizada: {dados}\n")
    self.output_text.see(tk.END)
    
    # Aplicar regras automaticamente
    if dados['valor'] < 30:
        # Enviar comando "01" para ligar a bomba 1
        self.mqtt_handler.publicar("bomba1", "01")
        self.output_text.insert(tk.END, "⚠️ Umidade baixa -> Bomba 1 LIGADA (comando: 01)\n")
    else:
        # Enviar comando "00" para desligar a bomba 1
        self.mqtt_handler.publicar("bomba1", "00")
        self.output_text.insert(tk.END, "⚠️ Umidade adequada -> Bomba 1 DESLIGADA (comando: 00)\n")
    self.output_text.see(tk.END)

def atualizar_umidade_solo2(self, dados):
    """Callback para atualizar dados de umidade do solo 2"""
    self.umidade_solo2_label.config(text=f"Umidade Solo 2: {dados['valor']}{dados['unidade']}")
    self.output_text.insert(tk.END, f"Umidade Solo 2 atualizada: {dados}\n")
    self.output_text.see(tk.END)
    
    # Aplicar regras automaticamente
    if dados['valor'] < 25:
        # Enviar comando "02" para ligar a bomba 2
        self.mqtt_handler.publicar("bomba2", "02")
        self.output_text.insert(tk.END, "⚠️ Umidade Solo 2 baixa -> Bomba 2 LIGADA (comando: 02)\n")
    else:
        # Enviar comando "00" para desligar a bomba 2
        self.mqtt_handler.publicar("bomba2", "00")
        self.output_text.insert(tk.END, "⚠️ Umidade Solo 2 adequada -> Bomba 2 DESLIGADA (comando: 00)\n")
    self.output_text.see(tk.END)

def atualizar_temperatura(self, dados):
    """Callback para atualizar dados de temperatura"""
    self.temperatura_label.config(text=f"Temperatura: {dados['valor']}{dados['unidade']}")
    self.output_text.insert(tk.END, f"Temperatura atualizada: {dados}\n")
    self.output_text.see(tk.END)
    
    # Aplicar regras automaticamente
    if dados['valor'] > 35:
        # Enviar comando "03" para ligar a bomba 3
        self.mqtt_handler.publicar("bomba3", "03")
        self.output_text.insert(tk.END, "⚠️ Temperatura alta -> Bomba 3 LIGADA (comando: 03)\n")
    else:
        # Enviar comando "00" para desligar a bomba 3
        self.mqtt_handler.publicar("bomba3", "00")
        self.output_text.insert(tk.END, "⚠️ Temperatura adequada -> Bomba 3 DESLIGADA (comando: 00)\n")
    self.output_text.see(tk.END) 