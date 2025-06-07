from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from tokens import Token

@dataclass
class ErroSemantico:
    linha: int
    mensagem: str
    tipo: str

class AnalisadorSemantico:
    def __init__(self):
        self.sensores_declarados: Dict[int, Dict] = {}
        self.dispositivos_utilizados: Set[str] = set()
        self.erros: List[ErroSemantico] = []
        self.regras: List[Dict] = []
        self.tempo_total: int = 0

    def analisar(self, ast: List[Dict]) -> Tuple[bool, List[ErroSemantico]]:
        """
        Realiza a análise semântica completa do AST.
        Retorna uma tupla (sucesso, lista_de_erros)
        """
        # Primeira passagem: coletar declarações e verificar estrutura básica
        for node in ast:
            if node['tipo'] == 'declaracao_sensor':
                self.verificar_declaracao_sensor(node)
            elif node['tipo'] == 'regra':
                self.verificar_regra(node)
                self.regras.append(node)
            elif node['tipo'] == 'espera':
                self.verificar_espera(node)

        # Segunda passagem: verificações de contexto e consistência
        self.verificar_consistencia_global()
        
        return len(self.erros) == 0, self.erros

    def verificar_declaracao_sensor(self, node: Dict):
        """Verifica a declaração de um sensor"""
        id_sensor = node['id']
        nome_sensor = node['nome']

        # Verificar ID único
        if id_sensor in self.sensores_declarados:
            self.adicionar_erro(
                node.get('linha', 0),
                f"O sensor com ID {id_sensor} já foi declarado anteriormente",
                "ID_DUPLICADO"
            )
            return

        # Verificar nome válido
        if not nome_sensor or len(nome_sensor.strip()) == 0:
            self.adicionar_erro(
                node.get('linha', 0),
                "O nome do sensor não pode estar vazio",
                "NOME_INVALIDO"
            )
            return

        # Verificar ID válido
        if id_sensor <= 0:
            self.adicionar_erro(
                node.get('linha', 0),
                f"O ID do sensor deve ser um número positivo, recebido: {id_sensor}",
                "ID_INVALIDO"
            )
            return

        self.sensores_declarados[id_sensor] = {
            'nome': nome_sensor,
            'regras': []
        }

    def verificar_regra(self, node: Dict):
        """Verifica uma regra de controle"""
        sensor_id = node['sensor_id']
        condicoes = node['condicoes']
        acao = node['acao']
        alvo = node['alvo']

        # Verificar se o sensor existe
        if sensor_id not in self.sensores_declarados:
            self.adicionar_erro(
                node.get('linha', 0),
                f"O sensor {sensor_id} não foi declarado antes de ser usado",
                "SENSOR_NAO_DECLARADO"
            )
            return

        # Verificar condições
        self.verificar_condicoes(condicoes, node.get('linha', 0))

        # Verificar ação e alvo
        if acao not in ['turn_on', 'turn_off']:
            self.adicionar_erro(
                node.get('linha', 0),
                f"Ação inválida: {acao}. Use 'turn_on' ou 'turn_off'",
                "ACAO_INVALIDA"
            )

        if not alvo or len(alvo.strip()) == 0:
            self.adicionar_erro(
                node.get('linha', 0),
                "O nome do dispositivo não pode estar vazio",
                "ALVO_INVALIDO"
            )

        self.dispositivos_utilizados.add(alvo)
        self.sensores_declarados[sensor_id]['regras'].append(node)

    def verificar_condicoes(self, condicoes: List, linha: int):
        """Verifica as condições de uma regra"""
        if not condicoes:
            self.adicionar_erro(
                linha,
                "A regra deve ter pelo menos uma condição",
                "CONDICAO_VAZIA"
            )
            return

        # Verificar primeira condição
        operador, limite = condicoes[0]
        self.verificar_operador_limite(operador, limite, linha)

        # Verificar condições adicionais
        for i in range(1, len(condicoes)):
            op_logico, operador, limite = condicoes[i]
            
            if op_logico not in ['PALAVRA_AND', 'PALAVRA_OR']:
                self.adicionar_erro(
                    linha,
                    f"Operador lógico inválido: {op_logico}. Use 'AND' ou 'OR'",
                    "OPERADOR_LOGICO_INVALIDO"
                )

            self.verificar_operador_limite(operador, limite, linha)

    def verificar_operador_limite(self, operador: str, limite: int, linha: int):
        """Verifica um operador e seu limite"""
        if operador not in ['<', '>', '<=', '>=', '==']:
            self.adicionar_erro(
                linha,
                f"Operador inválido: {operador}. Use '<', '>', '<=', '>=' ou '=='",
                "OPERADOR_INVALIDO"
            )

        if not isinstance(limite, (int, float)) or limite < 0 or limite > 100:
            self.adicionar_erro(
                linha,
                f"O limite deve ser um número entre 0 e 100, recebido: {limite}",
                "LIMITE_INVALIDO"
            )

    def verificar_espera(self, node: Dict):
        """Verifica um comando de espera"""
        duracao = node['duracao']

        if not isinstance(duracao, (int, float)) or duracao <= 0:
            self.adicionar_erro(
                node.get('linha', 0),
                f"A duração deve ser um número positivo, recebido: {duracao}",
                "DURACAO_INVALIDA"
            )

        self.tempo_total += duracao

    def verificar_consistencia_global(self):
        """Realiza verificações de consistência global"""
        # Verificar regras conflitantes
        self.verificar_regras_conflitantes()

        # Verificar tempo total
        if self.tempo_total > 3600:  # 1 hora
            self.adicionar_erro(
                0,
                f"O tempo total de espera ({self.tempo_total}s) excede o limite de 1 hora",
                "TEMPO_EXCESSIVO"
            )

        # Verificar dispositivos não utilizados
        for sensor_id, sensor in self.sensores_declarados.items():
            if not sensor['regras']:
                self.adicionar_erro(
                    0,
                    f"O sensor {sensor_id} ({sensor['nome']}) não é usado em nenhuma regra",
                    "SENSOR_NAO_UTILIZADO"
                )

    def verificar_regras_conflitantes(self):
        """Verifica se existem regras conflitantes para o mesmo dispositivo"""
        regras_por_dispositivo: Dict[str, List[Dict]] = {}

        for regra in self.regras:
            alvo = regra['alvo']
            if alvo not in regras_por_dispositivo:
                regras_por_dispositivo[alvo] = []
            regras_por_dispositivo[alvo].append(regra)

        for dispositivo, regras in regras_por_dispositivo.items():
            if len(regras) > 1:
                # Agrupar regras por ação (ligar/desligar)
                regras_ligar = [r for r in regras if r['acao'] == 'turn_on']
                regras_desligar = [r for r in regras if r['acao'] == 'turn_off']
                
                # Verificar se as condições são complementares
                for regra_ligar in regras_ligar:
                    for regra_desligar in regras_desligar:
                        # Se for o mesmo sensor
                        if regra_ligar['sensor_id'] == regra_desligar['sensor_id']:
                            # Verificar se as condições são complementares
                            cond_ligar = regra_ligar['condicoes'][0]
                            cond_desligar = regra_desligar['condicoes'][0]
                            
                            # Se não forem complementares, reportar erro
                            if not self.sao_condicoes_complementares(cond_ligar, cond_desligar):
                                self.adicionar_erro(
                                    0,
                                    f"O dispositivo '{dispositivo}' tem regras com condições não complementares",
                                    "REGRAS_CONFLITANTES"
                                )

    def sao_condicoes_complementares(self, cond1, cond2):
        """Verifica se duas condições são complementares"""
        op1, val1 = cond1
        op2, val2 = cond2
        
        # Verificar se os valores são iguais
        if val1 != val2:
            return False
            
        # Verificar se os operadores são complementares
        pares_complementares = [
            ('<', '>='),
            ('>', '<='),
            ('<=', '>'),
            ('>=', '<')
        ]
        
        return (op1, op2) in pares_complementares

    def adicionar_erro(self, linha: int, mensagem: str, tipo: str):
        """Adiciona um erro à lista de erros"""
        self.erros.append(ErroSemantico(linha, mensagem, tipo))

    def obter_resumo(self) -> str:
        """Retorna um resumo da análise semântica"""
        if not self.erros:
            return "✅ Análise semântica concluída sem erros"

        resumo = "❌ Análise semântica encontrou os seguintes erros:\n"
        for erro in self.erros:
            resumo += f"  - Linha {erro.linha}: {erro.mensagem} ({erro.tipo})\n"
        return resumo 