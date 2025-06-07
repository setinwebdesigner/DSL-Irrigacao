import paho.mqtt.client as mqtt
import time
import random

# Configuração do cliente MQTT
client = mqtt.Client()
broker = "localhost"  # Altere para o IP do seu broker MQTT
port = 1883

# Função para conectar ao broker
def conectar():
    try:
        client.connect(broker, port)
        print("Conectado ao broker MQTT!")
    except Exception as e:
        print(f"Erro ao conectar ao broker MQTT: {e}")

# Função para enviar comando para as bombas
def enviar_comando_bomba(bomba, comando):
    topico = f"bomba{bomba}"
    client.publish(topico, comando)
    print(f"Enviado comando {comando} para {topico}")

# Função para simular leitura dos sensores
def simular_sensores():
    # Simula valores entre 20 e 40 para os sensores
    umidade1 = random.randint(20, 40)
    umidade2 = random.randint(20, 40)
    temperatura = random.randint(30, 40)
    
    return umidade1, umidade2, temperatura

# Função para aplicar as regras de irrigação
def aplicar_regras(umidade1, umidade2, temperatura):
    print("\n=== Valores dos Sensores ===")
    print(f"Umidade Solo 1: {umidade1}%")
    print(f"Umidade Solo 2: {umidade2}%")
    print(f"Temperatura: {temperatura}°C")
    
    # Regras para a primeira área
    if umidade1 < 30:
        print("⚠️ Umidade Solo 1 baixa -> Ativando Bomba 1")
        enviar_comando_bomba(1, "01")
    else:
        print("✅ Umidade Solo 1 adequada -> Desativando Bomba 1")
        enviar_comando_bomba(1, "00")
    
    # Regras para a segunda área
    if umidade2 < 25:
        print("⚠️ Umidade Solo 2 baixa -> Ativando Bomba 2")
        enviar_comando_bomba(2, "02")
    else:
        print("✅ Umidade Solo 2 adequada -> Desativando Bomba 2")
        enviar_comando_bomba(2, "00")
    
    # Regras para controle de temperatura (Bomba 3)
    if temperatura > 35:
        print("⚠️ Temperatura alta -> Ativando Bomba 3")
        enviar_comando_bomba(3, "03")
    else:
        print("✅ Temperatura adequada -> Desativando Bomba 3")
        enviar_comando_bomba(3, "00")

# Conectar ao broker
conectar()

# Loop principal de simulação
try:
    print("\n=== Simulador de Irrigação ===")
    print("Pressione Ctrl+C para encerrar")
    
    while True:
        # Simula leitura dos sensores
        umidade1, umidade2, temperatura = simular_sensores()
        
        # Aplica as regras de irrigação
        aplicar_regras(umidade1, umidade2, temperatura)
        
        # Aguarda 5 segundos antes da próxima leitura
        print("\nAguardando 5 segundos para próxima leitura...")
        time.sleep(5)

except KeyboardInterrupt:
    print("\nPrograma encerrado pelo usuário")
finally:
    # Desliga todas as bombas antes de sair
    enviar_comando_bomba(1, "00")
    enviar_comando_bomba(2, "00")
    enviar_comando_bomba(3, "00")
    client.disconnect()
    print("Desconectado do broker MQTT") 