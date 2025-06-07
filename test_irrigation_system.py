import sys
import os
from irrigation_dsl import executar_sistema_irrigacao

def test_programa_basico():
    print("\n🧪 Teste 1: Programa Básico")
    programa = """
    SET SENSOR "Umidade" ID 1
    IF SENSOR 1 < 30 THEN TURN_ON "Bomba"
    WAIT 1
    IF SENSOR 1 > 80 THEN TURN_OFF "Bomba"
    """
    executar_sistema_irrigacao(programa)

def test_multiplos_sensores():
    print("\n🧪 Teste 2: Múltiplos Sensores")
    programa = """
    SET SENSOR "Umidade 1" ID 1
    SET SENSOR "Umidade 2" ID 2
    IF SENSOR 1 < 30 THEN TURN_ON "Bomba 1"
    IF SENSOR 2 < 25 THEN TURN_ON "Bomba 2"
    WAIT 1
    """
    executar_sistema_irrigacao(programa)

def test_tratamento_erros():
    print("\n🧪 Teste 3: Tratamento de Erros")
    # Teste com sensor não declarado
    programa = """
    IF SENSOR 1 < 30 THEN TURN_ON "Bomba"
    """
    try:
        executar_sistema_irrigacao(programa)
    except RuntimeError as e:
        print(f"✅ Erro capturado como esperado: {e}")

def test_regras_complexas():
    print("\n🧪 Teste 4: Regras Complexas com AND/OR")
    programa = """
    SET SENSOR "Temperatura" ID 1
    SET SENSOR "Umidade" ID 2
    IF SENSOR 1 > 35 AND >= 30 THEN TURN_ON "Ventilador"
    IF SENSOR 2 < 20 OR <= 25 THEN TURN_ON "Bomba"
    WAIT 1
    IF SENSOR 1 <= 25 THEN TURN_OFF "Ventilador"
    IF SENSOR 2 >= 70 THEN TURN_OFF "Bomba"
    """
    executar_sistema_irrigacao(programa)

def test_arquivo():
    print("\n🧪 Teste 5: Lendo do Arquivo")
    try:
        with open('example_program.txt', 'r') as file:
            programa = file.read()
        executar_sistema_irrigacao(programa)
    except FileNotFoundError:
        print("❌ Arquivo example_program.txt não encontrado")

def test_logs_e_estado():
    print("\n🧪 Teste 6: Verificação de Logs e Estado")
    programa = """
    SET SENSOR "Teste" ID 1
    IF SENSOR 1 < 50 AND > 20 THEN TURN_ON "Dispositivo"
    WAIT 1
    """
    executar_sistema_irrigacao(programa)
    
    # Verificar arquivo de log
    if os.path.exists("sistema_irrigacao.log"):
        print("✅ Arquivo de log criado com sucesso")
        with open("sistema_irrigacao.log", "r", encoding="utf-8") as f:
            print("\nÚltimas linhas do log:")
            lines = f.readlines()[-3:]  # Mostrar últimas 3 linhas
            for line in lines:
                print(f"  {line.strip()}")
    else:
        print("❌ Arquivo de log não encontrado")
    
    # Verificar arquivo de estado
    if os.path.exists("estado_sistema.json"):
        print("\n✅ Arquivo de estado criado com sucesso")
        with open("estado_sistema.json", "r", encoding="utf-8") as f:
            print("\nEstado atual do sistema:")
            print(f.read())
    else:
        print("❌ Arquivo de estado não encontrado")

if __name__ == "__main__":
    print("🧪 Iniciando Testes do Sistema de Irrigação")
    print("=" * 50)

    testes = [
        test_programa_basico,
        test_multiplos_sensores,
        test_tratamento_erros,
        test_regras_complexas,
        test_arquivo,
        test_logs_e_estado
    ]

    for teste in testes:
        try:
            teste()
            print("-" * 50)
        except Exception as e:
            print(f"❌ Erro no teste {teste.__name__}: {e}")
            print("-" * 50)

    print("\n✨ Testes concluídos!")
    
    # Limpar arquivos temporários após os testes
    print("\n🧹 Limpando arquivos temporários...")
    arquivos_temp = ["sistema_irrigacao.log", "estado_sistema.json"]
    for arquivo in arquivos_temp:
        if os.path.exists(arquivo):
            try:
                os.remove(arquivo)
                print(f"✅ Arquivo {arquivo} removido")
            except Exception as e:
                print(f"❌ Erro ao remover {arquivo}: {e}")
    
    print("\n🏁 Finalizado!") 