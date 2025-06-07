from irrigation_dsl import executar_sistema_irrigacao

# Programa de irrigação
programa = """
SET SENSOR "Umidade Solo 1" ID 1
SET SENSOR "Umidade Solo 2" ID 2
SET SENSOR "Temperatura" ID 3

# Regras para a primeira área
IF SENSOR 1 < 30 THEN TURN_ON "Bomba 1"
IF SENSOR 1 >= 30 THEN TURN_OFF "Bomba 1"

# Regras para a segunda área
IF SENSOR 2 < 25 THEN TURN_ON "Bomba 2"
IF SENSOR 2 >= 25 THEN TURN_OFF "Bomba 2"

# Regras para controle de temperatura
IF SENSOR 3 > 35 THEN TURN_ON "Ventilador"
IF SENSOR 3 <= 35 THEN TURN_OFF "Ventilador"

WAIT 5
"""

# Executar o programa
executar_sistema_irrigacao(programa)