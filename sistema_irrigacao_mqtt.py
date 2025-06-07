import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

class SistemaIrrigacaoMQTT:
    def __init__(self):
        # Configuração do cliente MQTT
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Dados dos sensores
        self.sensores = {
            "umidade": {"valor": 0, "unidade": "%"},
            "temperatura": {"valor": 0, "unidade": "C"},
            "bomba": {"estado": "desligada"}
        }
        
        # Regras do sistema
        self.regras = {
            "umidade": {
                "minima": 30,  # Se umidade < 30%, liga a bomba
                "maxima": 70   # Se umidade > 70%, desliga a bomba
            },
            "temperatura": {
                "maxima": 35,  # Se temperatura > 35°C, liga o ventilador
                "minima": 25   # Se temperatura < 25°C, desliga o ventilador
            }
        }
        
        # Conectar ao broker MQTT
        try:
            self.client.connect("localhost", 1883)
            self.client.loop_start()
            print("✅ Conectado ao broker MQTT!")
        except Exception as e:
            print(f"❌ Erro ao conectar ao broker MQTT: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Conectado ao broker MQTT!")
            # Inscrever nos tópicos
            self.client.subscribe("umidade")
            self.client.subscribe("temperatura")
            self.client.subscribe("bomba")
        else:
            print(f"❌ Falha na conexão com o broker MQTT. Código: {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            # Decodificar mensagem
            payload = json.loads(msg.payload.decode())
            topico = msg.topic
            
            # Atualizar dados do sensor
            if topico == "umidade":
                self.sensores["umidade"] = payload
                self.verificar_regra_umidade()
            
            elif topico == "temperatura":
                self.sensores["temperatura"] = payload
                self.verificar_regra_temperatura()
            
            elif topico == "bomba":
                self.sensores["bomba"] = payload
            
            # Mostrar dados atualizados
            self.mostrar_status()
            
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar mensagem: {msg.payload}")
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
    
    def verificar_regra_umidade(self):
        """Verifica as regras de umidade e controla a bomba"""
        umidade = self.sensores["umidade"]["valor"]
        
        if umidade < self.regras["umidade"]["minima"]:
            self.acionar_bomba("ligada")
            print(f"⚠️ Umidade baixa ({umidade}%) -> Bomba LIGADA")
        
        elif umidade > self.regras["umidade"]["maxima"]:
            self.acionar_bomba("desligada")
            print(f"⚠️ Umidade alta ({umidade}%) -> Bomba DESLIGADA")
    
    def verificar_regra_temperatura(self):
        """Verifica as regras de temperatura e controla o ventilador"""
        temperatura = self.sensores["temperatura"]["valor"]
        
        if temperatura > self.regras["temperatura"]["maxima"]:
            self.acionar_ventilador("ligado")
            print(f"⚠️ Temperatura alta ({temperatura}°C) -> Ventilador LIGADO")
        
        elif temperatura < self.regras["temperatura"]["minima"]:
            self.acionar_ventilador("desligado")
            print(f"⚠️ Temperatura baixa ({temperatura}°C) -> Ventilador DESLIGADO")
    
    def acionar_bomba(self, estado):
        """Aciona a bomba e publica o estado"""
        self.sensores["bomba"]["estado"] = estado
        self.client.publish("bomba", json.dumps({"estado": estado}))
    
    def acionar_ventilador(self, estado):
        """Aciona o ventilador e publica o estado"""
        self.client.publish("ventilador", json.dumps({"estado": estado}))
    
    def mostrar_status(self):
        """Mostra o status atual do sistema"""
        print("\n" + "="*50)
        print(f"Status do Sistema - {datetime.now().strftime('%H:%M:%S')}")
        print("="*50)
        print(f"Umidade: {self.sensores['umidade']['valor']}{self.sensores['umidade']['unidade']}")
        print(f"Temperatura: {self.sensores['temperatura']['valor']}{self.sensores['temperatura']['unidade']}")
        print(f"Bomba: {self.sensores['bomba']['estado']}")
        print("="*50 + "\n")
    
    def desconectar(self):
        """Desconecta do broker MQTT"""
        self.client.loop_stop()
        self.client.disconnect()
        print("✅ Desconectado do broker MQTT")

def main():
    # Criar e iniciar o sistema
    sistema = SistemaIrrigacaoMQTT()
    
    try:
        print("\n🔄 Sistema de Irrigação iniciado!")
        print("Aguardando dados dos sensores...")
        print("Pressione Ctrl+C para encerrar\n")
        
        # Manter o programa rodando
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Encerrando o sistema...")
        sistema.desconectar()
        print("✅ Sistema encerrado!")

if __name__ == "__main__":
    main() 