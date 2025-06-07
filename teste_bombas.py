import paho.mqtt.client as mqtt
import time

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

# Conectar ao broker
conectar()

# Loop principal de teste
try:
    print("\n=== Teste de Controle de Bombas ===")
    print("1 - Ligar Bomba 1")
    print("2 - Ligar Bomba 2")
    print("3 - Ligar Bomba 3")
    print("0 - Desligar todas as bombas")
    print("q - Sair")
    
    while True:
        comando = input("\nDigite o comando (1,2,3,0,q): ").lower()
        
        if comando == 'q':
            break
        elif comando == '1':
            enviar_comando_bomba(1, "01")
        elif comando == '2':
            enviar_comando_bomba(2, "02")
        elif comando == '3':
            enviar_comando_bomba(3, "03")
        elif comando == '0':
            # Desliga todas as bombas
            enviar_comando_bomba(1, "00")
            enviar_comando_bomba(2, "00")
            enviar_comando_bomba(3, "00")
        else:
            print("Comando inválido!")
        
        time.sleep(0.5)  # Pequena pausa entre comandos

except KeyboardInterrupt:
    print("\nPrograma encerrado pelo usuário")
finally:
    client.disconnect()
    print("Desconectado do broker MQTT") 