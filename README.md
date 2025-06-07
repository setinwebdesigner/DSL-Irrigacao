# Sistema de Irrigação DSL 🌱

Este é um projeto de uma Linguagem de Domínio Específico (DSL) para controle de sistemas de irrigação. O projeto foi desenvolvido como parte da disciplina de Teoria da Computação e Compiladores.

## 📋 Sobre o Projeto

O projeto implementa uma linguagem simples para definir regras de irrigação baseadas em leituras de sensores de umidade. A linguagem permite:

- Declarar sensores
- Definir regras de ativação/desativação com condições lógicas (AND/OR)
- Configurar tempos de espera
- Registrar histórico de operações
- Salvar estado do sistema

## 🔧 Componentes do Sistema

### 1. Analisador Léxico (Lexer)
- Responsável por quebrar o texto do programa em tokens
- Identifica palavras-chave, números, strings e operadores
- Mantém controle da linha atual para mensagens de erro
- Suporte a operadores lógicos (AND, OR)

### 2. Analisador Sintático (Parser)
- Verifica se a sequência de tokens forma comandos válidos
- Gera uma árvore de sintaxe abstrata (AST)
- Implementa validação de sintaxe para cada tipo de comando
- Suporta condições compostas com AND/OR

### 3. Máquina Virtual
- Executa os comandos da linguagem
- Simula leituras de sensores
- Controla dispositivos (bombas, nebulizadores, etc.)
- Registra histórico de operações em arquivo
- Salva estado do sistema em JSON

## 📝 Sintaxe da Linguagem

### Declaração de Sensor
```
SET SENSOR "nome" ID número
```

### Regra de Ativação/Desativação (com lógica)
```
IF SENSOR id operador valor [AND|OR operador valor]* THEN TURN_ON|TURN_OFF "dispositivo"
```

### Comando de Espera
```
WAIT segundos
```

## 🚀 Como Usar

1. Instale o Python 3.7 ou superior
2. Execute o arquivo `irrigation_dsl.py`
3. O programa já inclui um exemplo básico de uso
4. Os logs são salvos em `sistema_irrigacao.log`
5. O estado do sistema é salvo em `estado_sistema.json`

### Exemplo de Programa com Lógica
```
SET SENSOR "Umidade" ID 1
IF SENSOR 1 < 30 AND > 10 THEN TURN_ON "Bomba"
WAIT 2
IF SENSOR 1 > 80 OR >= 75 THEN TURN_OFF "Bomba"
```

## 🎯 Funcionalidades

- ✅ Análise léxica com detecção de tokens
- ✅ Análise sintática com validação de regras
- ✅ Execução simulada de comandos
- ✅ Tratamento de erros robusto
- ✅ Simulação de leituras de sensores
- ✅ Operadores lógicos (AND, OR)
- ✅ Registro de histórico em arquivo
- ✅ Persistência de estado em JSON

## 🔍 Detalhes Técnicos

### Tokens Suportados
- Palavras-chave: SET, SENSOR, ID, IF, THEN, TURN_ON, TURN_OFF, WAIT, AND, OR
- Strings: Entre aspas duplas
- Números: Inteiros
- Operadores: <, >, <=, >=, ==

### Estrutura do AST
Cada comando é convertido em um dicionário com informações relevantes:
- Declarações de sensor: tipo, nome, ID
- Regras: tipo, sensor_id, condições (lista de operadores e valores), ação, alvo
- Espera: tipo, duração

### Sistema de Logs
- Registro de todas as operações com timestamp
- Formato: "YYYY-MM-DD HH:MM:SS - Mensagem"
- Arquivo: sistema_irrigacao.log

### Estado do Sistema
- Salvo em JSON após cada execução
- Contém estado atual de sensores e dispositivos
- Inclui timestamp da última atualização
- Arquivo: estado_sistema.json

## 📚 Contribuições para Avaliação

1. **Entregas do Projeto (1,0)**
   - Código fonte comentado em português
   - Documentação completa
   - Exemplos de uso
   - Sistema de logs e persistência

2. **Apresentação e Arguição (3,0)**
   - Demonstração do funcionamento
   - Explicação dos componentes
   - Discussão das decisões de design
   - Demonstração das melhorias implementadas

3. **Nível de Impacto (3,0)**
   - DSL prática e útil
   - Implementação completa e robusta
   - Tratamento de erros avançado
   - Recursos adicionais (logs, estado, operadores lógicos)

4. **Artigo (3,0)**
   - Descrição técnica detalhada
   - Fundamentação teórica
   - Resultados e conclusões
   - Análise das melhorias implementadas # DSL-Irrigacao
