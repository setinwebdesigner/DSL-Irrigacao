from irrigation_dsl import executar_sistema_irrigacao

# Programa de irrigação inteligente
programa = """
# Declaração dos sensores
SET SENSOR "Umidade Solo 1" ID 1
SET SENSOR "Umidade Solo 2" ID 2
SET SENSOR "Temperatura" ID 3

# Regras para a primeira área
IF SENSOR 1 < 30 THEN TURN_ON "Bomba 1"
WAIT 5
IF SENSOR 1 > 70 THEN TURN_OFF "Bomba 1"

# Regras para a segunda área
IF SENSOR 2 < 25 THEN TURN_ON "Bomba 2"
WAIT 5
IF SENSOR 2 > 65 THEN TURN_OFF "Bomba 2"

# Regras para controle de temperatura
IF SENSOR 3 > 35 THEN TURN_ON "Ventilador"
IF SENSOR 3 < 25 THEN TURN_OFF "Ventilador"

# Regra para sistema de emergência (umidade muito baixa)
IF SENSOR 1 < 20 THEN TURN_ON "Sistema de Emergência"
IF SENSOR 2 < 20 THEN TURN_ON "Sistema de Emergência"

# Espera final
WAIT 10
"""

print("🌱 Sistema de Irrigação Inteligente")
print("=" * 50)
print("\n📋 Programa a ser executado:")
print(programa)
print("\n▶️ Iniciando execução...\n")

# Executar o programa
executar_sistema_irrigacao(programa) 