import re
from dataclasses import dataclass
from typing import List, Dict
import random
import time
from datetime import datetime
import json
import os
from semantic_analyzer import AnalisadorSemantico
from tokens import Token

class AnalisadorLexico:
    def __init__(self, texto: str):
        self.texto = texto
        self.posicao = 0
        self.linha_atual = 1
        self.tokens = []
        
    def tokenizar(self) -> List[Token]:
        # Padrões de tokens
        padroes = [
            ('PALAVRA_SET', r'INSERIR'),
            ('PALAVRA_SENSOR', r'SENSOR'),
            ('PALAVRA_ID', r'ID'),
            ('PALAVRA_IF', r'SE'),
            ('PALAVRA_THEN', r'ENTAO'),
            ('PALAVRA_TURN_ON', r'LIGAR'),
            ('PALAVRA_TURN_OFF', r'DESLIGAR'),
            ('PALAVRA_WAIT', r'ESPERAR'),
            ('PALAVRA_AND', r'E'), 
            ('PALAVRA_OR', r'OU'),   
            ('TEXTO', r'"[^"]*"'),
            ('NUMERO', r'\d+'),
            ('OPERADOR', r'[<>]=?|=='),
            ('ESPACO', r'[ \t]+'),
            ('NOVA_LINHA', r'\n'),
        ]
        
        # Combinar padrões
        regex_token = '|'.join(f'(?P<{nome}>{padrao})' for nome, padrao in padroes)
        
        for match in re.finditer(regex_token, self.texto):
            tipo_token = match.lastgroup
            valor_token = match.group()
            
            if tipo_token == 'NOVA_LINHA':
                self.linha_atual += 1
                continue
            elif tipo_token == 'ESPACO':
                continue
                
            self.tokens.append(Token(tipo_token, valor_token, self.linha_atual))
            
        return self.tokens

class AnalisadorSintatico:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicao = 0
        self.ast = []
        
    def analisar(self):
        while self.posicao < len(self.tokens):
            if self.token_atual().tipo == 'PALAVRA_SET':
                self.ast.append(self.analisar_declaracao_sensor())
            elif self.token_atual().tipo == 'PALAVRA_IF':
                self.ast.append(self.analisar_regra())
            elif self.token_atual().tipo == 'PALAVRA_WAIT':
                self.ast.append(self.analisar_espera())
            else:
                raise SyntaxError(f"Token inesperado: {self.token_atual()}")
                
        return self.ast
    
    def token_atual(self) -> Token:
        return self.tokens[self.posicao]
    
    def avancar(self):
        self.posicao += 1
        
    def analisar_declaracao_sensor(self):
        self.avancar()  # pular INSERIR
        if self.token_atual().tipo != 'PALAVRA_SENSOR':
            raise SyntaxError("Esperava palavra-chave SENSOR")
        self.avancar()
        
        if self.token_atual().tipo != 'TEXTO':
            raise SyntaxError("Esperava nome do sensor entre aspas")
        nome_sensor = self.token_atual().valor.strip('"')
        self.avancar()
        
        if self.token_atual().tipo != 'PALAVRA_ID':
            raise SyntaxError("Esperava palavra-chave ID")
        self.avancar()
        
        if self.token_atual().tipo != 'NUMERO':
            raise SyntaxError("Esperava número de ID do sensor")
        id_sensor = int(self.token_atual().valor)
        self.avancar()
        
        return {
            'tipo': 'declaracao_sensor',
            'nome': nome_sensor,
            'id': id_sensor
        }
    
    def analisar_regra(self):
        self.avancar()  # pular SE
        
        if self.token_atual().tipo != 'PALAVRA_SENSOR':
            raise SyntaxError("Esperava palavra-chave SENSOR")
        self.avancar()
        
        if self.token_atual().tipo != 'NUMERO':
            raise SyntaxError("Esperava ID do sensor")
        id_sensor = int(self.token_atual().valor)
        self.avancar()
        
        if self.token_atual().tipo != 'OPERADOR':
            raise SyntaxError("Esperava operador de comparação")
        operador = self.token_atual().valor
        self.avancar()
        
        if self.token_atual().tipo != 'NUMERO':
            raise SyntaxError("Esperava valor limite")
        limite = int(self.token_atual().valor)
        self.avancar()
        
        # Suporte para operadores lógicos E e OU
        condicoes = [(operador, limite)]
        while self.posicao < len(self.tokens) and self.token_atual().tipo in ['PALAVRA_AND', 'PALAVRA_OR']:
            operador_logico = self.token_atual().tipo
            self.avancar()
            
            if self.token_atual().tipo != 'OPERADOR':
                raise SyntaxError("Esperava operador de comparação após E/OU")
            novo_operador = self.token_atual().valor
            self.avancar()
            
            if self.token_atual().tipo != 'NUMERO':
                raise SyntaxError("Esperava valor limite após operador")
            novo_limite = int(self.token_atual().valor)
            self.avancar()
            
            condicoes.append((operador_logico, novo_operador, novo_limite))
        
        if self.token_atual().tipo != 'PALAVRA_THEN':
            raise SyntaxError("Esperava palavra-chave ENTAO")
        self.avancar()
        
        if self.token_atual().tipo not in ['PALAVRA_TURN_ON', 'PALAVRA_TURN_OFF']:
            raise SyntaxError("Esperava ação LIGAR ou DESLIGAR")
        acao = self.token_atual().tipo.replace('PALAVRA_', '').lower()
        self.avancar()
        
        if self.token_atual().tipo != 'TEXTO':
            raise SyntaxError("Esperava nome do dispositivo entre aspas")
        alvo = self.token_atual().valor.strip('"')
        self.avancar()
        
        return {
            'tipo': 'regra',
            'sensor_id': id_sensor,
            'condicoes': condicoes,
            'acao': acao,
            'alvo': alvo
        }
    
    def analisar_espera(self):
        self.avancar()  # pular ESPERAR
        
        if self.token_atual().tipo != 'NUMERO':
            raise SyntaxError("Esperava duração da espera em segundos")
        duracao = int(self.token_atual().valor)
        self.avancar()
        
        return {
            'tipo': 'espera',
            'duracao': duracao
        }

class MaquinaVirtual:
    def __init__(self, arquivo_log=None):
        self.sensores = {}
        self.dispositivos = {}
        self.arquivo_log = arquivo_log or "sistema_irrigacao.log"
        self.historico = []
        
    def executar(self, ast):
        for node in ast:
            if node['tipo'] == 'declaracao_sensor':
                self.declarar_sensor(node)
            elif node['tipo'] == 'regra':
                self.executar_regra(node)
            elif node['tipo'] == 'espera':
                self.executar_espera(node)
        
        # Salvar histórico ao final da execução
        self.salvar_historico()
                
    def declarar_sensor(self, node):
        id_sensor = node['id']
        self.sensores[id_sensor] = {
            'nome': node['nome'],
            'valor': random.randint(0, 100)  # Simular leitura do sensor
        }
        mensagem = f"✅ Sensor '{node['nome']}' (ID: {id_sensor}) declarado com sucesso"
        print(mensagem)
        self.registrar_evento(mensagem)
        
    def executar_regra(self, node):
        id_sensor = node['sensor_id']
        if id_sensor not in self.sensores:
            raise RuntimeError(f"Erro: Sensor {id_sensor} não encontrado")
            
        valor_sensor = self.sensores[id_sensor]['valor']
        mensagem = f"📊 Leitura do sensor {id_sensor}: {valor_sensor}%"
        print(mensagem)
        self.registrar_evento(mensagem)
        
        condicao_satisfeita = self.avaliar_condicoes(valor_sensor, node['condicoes'])
        
        if condicao_satisfeita:
            if node['acao'] == 'turn_on':
                mensagem = f"🟢 Ligando o dispositivo: {node['alvo']}"
                self.dispositivos[node['alvo']] = True
            else:
                mensagem = f"🔴 Desligando o dispositivo: {node['alvo']}"
                self.dispositivos[node['alvo']] = False
            print(mensagem)
            self.registrar_evento(mensagem)
                
    def avaliar_condicoes(self, valor, condicoes):
        resultado = self.avaliar_condicao(valor, condicoes[0][0], condicoes[0][1])
        
        for condicao in condicoes[1:]:
            op_logico, operador, limite = condicao
            novo_resultado = self.avaliar_condicao(valor, operador, limite)
            
            if op_logico == 'PALAVRA_AND':
                resultado = resultado and novo_resultado
            else:  # OR
                resultado = resultado or novo_resultado
                
        return resultado
    
    def avaliar_condicao(self, valor, operador, limite):
        if operador == '<':
            return valor < limite
        elif operador == '>':
            return valor > limite
        elif operador == '<=':
            return valor <= limite
        elif operador == '>=':
            return valor >= limite
        elif operador == '==':
            return valor == limite
        else:
            raise RuntimeError(f"Erro: Operador desconhecido: {operador}")
            
    def executar_espera(self, node):
        duracao = node['duracao']
        mensagem = f"⏳ Aguardando {duracao} segundos..."
        print(mensagem)
        self.registrar_evento(mensagem)
        time.sleep(duracao)
        
    def registrar_evento(self, mensagem):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.historico.append({
            'timestamp': timestamp,
            'mensagem': mensagem
        })
        
    def salvar_historico(self):
        with open(self.arquivo_log, 'a', encoding='utf-8') as f:
            for evento in self.historico:
                f.write(f"{evento['timestamp']} - {evento['mensagem']}\n")
        
        # Salvar estado atual em JSON
        estado = {
            'sensores': self.sensores,
            'dispositivos': self.dispositivos,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open('estado_sistema.json', 'w', encoding='utf-8') as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)

def executar_sistema_irrigacao(programa: str):
    print("🌱 Iniciando Sistema de Irrigação")
    print("--------------------------------------------------\n")
    
    print("📝 Realizando Análise Léxica...")
    analisador_lexico = AnalisadorLexico(programa)
    tokens = analisador_lexico.tokenizar()
    
    print("🔍 Analisando programa...")
    analisador_sintatico = AnalisadorSintatico(tokens)
    ast = analisador_sintatico.analisar()
    
    # Adicionar análise semântica
    print("🔎 Realizando Análise Semântica...")
    analisador_semantico = AnalisadorSemantico()
    sucesso, erros = analisador_semantico.analisar(ast)
    
    if not sucesso:
        print("\n❌ Erros encontrados na análise semântica:")
        for erro in erros:
            print(f"  - Linha {erro.linha}: {erro.mensagem}")
        return
    
    print("✅ Análise semântica concluída com sucesso")
    
    print("\n▶️ Executando programa...")
    maquina = MaquinaVirtual()
    try:
        maquina.executar(ast)
    except Exception as e:
        print(f"❌ Erro durante a execução: {str(e)}")
        return
    
    print("\n✨ Execução do programa concluída")
    print("------------------------------------------------")

# Exemplo de uso
if __name__ == "__main__":
    programa = """
    SET SENSOR "Umidade" ID 1
    IF SENSOR 1 < 30 AND > 10 THEN TURN_ON "Bomba"
    WAIT 2
    IF SENSOR 1 > 80 OR >= 75 THEN TURN_OFF "Bomba"
    """
    
    executar_sistema_irrigacao(programa) 