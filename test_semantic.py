import os
import sys
from irrigation_dsl import executar_sistema_irrigacao

# Verifica se já existe uma instância rodando
if os.path.exists("irrigacao.lock"):
    print("⚠️ O sistema já está em execução!")
    sys.exit(1)

# Cria arquivo de lock
with open("irrigacao.lock", "w") as f:
    f.write(str(os.getpid()))

try:
    def test_analise_semantica():
        print("\n🧪 Testando Análise Semântica")
        print("=" * 50)

        # Teste 1: Programa válido
        print("\n📌 Teste 1: Programa válido")
        programa_valido = """
        SET SENSOR "Umidade" ID 1
        IF SENSOR 1 < 30 THEN TURN_ON "Bomba"
        WAIT 5
        IF SENSOR 1 > 70 THEN TURN_OFF "Bomba"
        """
        executar_sistema_irrigacao(programa_valido)

        # Teste 2: Sensor não declarado
        print("\n📌 Teste 2: Sensor não declarado")
        programa_sensor_nao_declarado = """
        IF SENSOR 1 < 30 THEN TURN_ON "Bomba"
        """
        executar_sistema_irrigacao(programa_sensor_nao_declarado)

        # Teste 3: ID duplicado
        print("\n📌 Teste 3: ID duplicado")
        programa_id_duplicado = """
        SET SENSOR "Umidade 1" ID 1
        SET SENSOR "Umidade 2" ID 1
        """
        executar_sistema_irrigacao(programa_id_duplicado)

        # Teste 4: Regras conflitantes
        print("\n📌 Teste 4: Regras conflitantes")
        programa_regras_conflitantes = """
        SET SENSOR "Umidade" ID 1
        IF SENSOR 1 < 30 THEN TURN_ON "Bomba"
        IF SENSOR 1 > 20 THEN TURN_OFF "Bomba"
        """
        executar_sistema_irrigacao(programa_regras_conflitantes)

        # Teste 5: Limite inválido
        print("\n📌 Teste 5: Limite inválido")
        programa_limite_invalido = """
        SET SENSOR "Umidade" ID 1
        IF SENSOR 1 < 150 THEN TURN_ON "Bomba"
        """
        executar_sistema_irrigacao(programa_limite_invalido)

        # Teste 6: Tempo excessivo
        print("\n📌 Teste 6: Tempo excessivo")
        programa_tempo_excessivo = """
        SET SENSOR "Umidade" ID 1
        WAIT 4000
        """
        executar_sistema_irrigacao(programa_tempo_excessivo)

    test_analise_semantica()

finally:
    # Remove o arquivo de lock ao finalizar
    if os.path.exists("irrigacao.lock"):
        os.remove("irrigacao.lock") 