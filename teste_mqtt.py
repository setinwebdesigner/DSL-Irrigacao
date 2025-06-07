import paho.mqtt.client as mqtt
import json
import time
import subprocess
import os

MOSQUITTO_PATH = r"C:\Program Files\mosquitto"

def publicar_mosquitto(topico, mensagem):
    """Publica mensagem usando mosquitto_pub diretamente"""
    mosquitto_pub = os.path.join(MOSQUITTO_PATH, "mosquitto_pub.exe")
    try:
        comando = [mosquitto_pub, "-t", topico, "-m", json.dumps(mensagem)]
        subprocess.run(comando, check=True)
        print(f"Mensagem publicada em {topico}: {mensagem}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao publicar com mosquitto_pub: {e}")
    except Exception as e:
        print(f"Erro ao executar mosquitto_pub: {e}")

def publicar_paho(topico, mensagem):
    """Publica mensagem usando a biblioteca paho-mqtt"""
    client = mqtt.Client()
    try:
        client.connect("localhost", 1883)
        client.publish(topico, json.dumps(mensagem))
        print(f"Mensagem publicada em {topico}: {mensagem}")
    except Exception as e:
        print(f"Erro ao publicar com paho-mqtt: {e}")
    finally:
        client.disconnect()

def publicar_dados():
    # Criar cliente MQTT
    client = mqtt.Client()
    
    try:
        # Conectar ao broker
        client.connect("localhost", 1883)
        print("✅ Conectado ao broker MQTT!")
        
        # Dados de teste
        dados_teste = [
            # Teste 1: Umidade baixa
            {"topico": "umidade", "dados": {"valor": 25, "unidade": "%"}},
            
            # Teste 2: Umidade alta
            {"topico": "umidade", "dados": {"valor": 75, "unidade": "%"}},
            
            # Teste 3: Temperatura alta
            {"topico": "temperatura", "dados": {"valor": 40, "unidade": "C"}},
            
            # Teste 4: Temperatura normal
            {"topico": "temperatura", "dados": {"valor": 30, "unidade": "C"}}
        ]
        
        # Enviar cada conjunto de dados
        for teste in dados_teste:
            print(f"\n📤 Enviando dados para {teste['topico']}:")
            print(f"Dados: {teste['dados']}")
            
            # Publicar dados
            client.publish(
                teste['topico'],
                json.dumps(teste['dados'])
            )
            
            # Aguardar 5 segundos entre cada envio
            time.sleep(5)
        
        print("\n✅ Todos os testes foram enviados!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        # Desconectar
        client.disconnect()
        print("✅ Desconectado do broker MQTT")

def main():
    print("Testando publicação MQTT...")
    print("Usando mosquitto_pub de:", MOSQUITTO_PATH)
    
    # Teste 1: Formato completo
    print("\n1. Testando formato completo:")
    publicar_mosquitto("umidade", {"valor": 65, "unidade": "%"})
    publicar_mosquitto("temperatura", {"valor": 25, "unidade": "C"})
    publicar_mosquitto("bomba", {"estado": "ligada"})
    
    time.sleep(2)
    
    # Teste 2: Formato simples
    print("\n2. Testando formato simples:")
    publicar_mosquitto("umidade", 70)
    publicar_mosquitto("temperatura", 30)
    publicar_mosquitto("bomba", 1)
    
    time.sleep(2)
    
    # Teste 3: Formato alternativo
    print("\n3. Testando formato alternativo:")
    publicar_mosquitto("umidade", {"umidade": 75})
    publicar_mosquitto("temperatura", {"temperatura": 28})
    publicar_mosquitto("bomba", {"status": 1})
    
    print("\nTestando também com paho-mqtt como backup...")
    publicar_paho("umidade", {"valor": 80, "unidade": "%"})
    publicar_paho("temperatura", {"valor": 30, "unidade": "C"})
    publicar_paho("bomba", {"estado": "desligada"})

if __name__ == "__main__":
    publicar_dados() 