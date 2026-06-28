import re
import sys

# =============================================================================
# 1. DEFINIÇÃO DOS TOKENS
# =============================================================================
# Constantes que identificam a classe/tipo de cada token reconhecido pelo analisador.
TOKEN_NUM   = 'NUM'    # Representa números (inteiros e decimais)
TOKEN_SOMA  = 'SOMA'   # Representa o operador '+'
TOKEN_MULT  = 'MULT'   # Representa o operador '*'
TOKEN_APAR  = 'APAR'   # Representa o parêntese esquerdo '('
TOKEN_FPAR  = 'FPAR'   # Representa o parêntese direito ')'

class Token:
    """Classe que representa a menor unidade sintática (token) encontrada na entrada."""
    def __init__(self, tipo, valor, posicao):
        self.tipo = tipo        # Tipo do token (ex: 'NUM', 'SOMA')
        self.valor = valor      # A string literal correspondente (ex: '2.5', '+')
        self.posicao = posicao  # O índice/posição do caractere inicial no código fonte original

    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}')"

# =============================================================================
# 2. ANALISADOR LÉXICO (LEXER)
# =============================================================================
def lexer(codigo_fonte):
    """
    Analisa a string de entrada e gera uma sequência (lista) de objetos Token.
    Usa Expressões Regulares (RegEx) para casar os padrões e ignorar espaços em branco.
    """
    tokens = []
    i = 0
    tamanho = len(codigo_fonte)

    # Expressões regulares compiladas ancoradas no início (^) para casar substrings
    regex_num = re.compile(r'^[0-9]+(?:\.[0-9]+)?') # Múltiplos dígitos e opcionalmente decimais (.99)
    regex_soma = re.compile(r'^\+')
    regex_mult = re.compile(r'^\*')
    regex_apar = re.compile(r'^\(')
    regex_fpar = re.compile(r'^\)')
    regex_espaco = re.compile(r'^\s+')              # Padrão para espaços vazios (transparência de espaços)

    while i < tamanho:
        # Pega a fatia do código fonte da posição atual até o fim
        sub_string = codigo_fonte[i:]

        # 1. Ignora espaços em branco (não geram tokens)
        match_espaco = regex_espaco.match(sub_string)
        if match_espaco:
            i += len(match_espaco.group(0))
            continue

        # 2. Reconhecimento de números inteiros e de ponto flutuante
        match_num = regex_num.match(sub_string)
        if match_num:
            valor = match_num.group(0)
            tokens.append(Token(TOKEN_NUM, valor, i))
            i += len(valor)
            continue

        # 3. Reconhecimento dos demais símbolos individuais
        if regex_soma.match(sub_string):
            tokens.append(Token(TOKEN_SOMA, '+', i))
            i += 1
            continue

        if regex_mult.match(sub_string):
            tokens.append(Token(TOKEN_MULT, '*', i))
            i += 1
            continue

        if regex_apar.match(sub_string):
            tokens.append(Token(TOKEN_APAR, '(', i))
            i += 1
            continue

        if regex_fpar.match(sub_string):
            tokens.append(Token(TOKEN_FPAR, ')', i))
            i += 1
            continue

        # Caso nenhum padrão de caractere seja reconhecido, levanta erro léxico
        raise Exception(f"Erro Léxico: Caractere inválido '{codigo_fonte[i]}' na posição {i}.")

    return tokens

# =============================================================================
# 3. PARSER E GERADOR DE CÓDIGO INTERMEDIÁRIO (LL(1))
# =============================================================================
class Parser:
    """
    Analisador Sintático Preditivo Recursivo LL(1).
    Realiza a validação sintática, interpretação semântica e geração de Código de Três Endereços (C3E).
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0               # Ponteiro para o token corrente
        self.contador_temp = 0     # Usado para numerar os registradores temporários (t0, t1, ...)
        self.instrucoes_c3e = []   # Armazena as instruções do Código de Três Endereços geradas

    def novo_temporario(self):
        """Gera um nome de variável temporária inédito para a linearização de instruções."""
        nome = f"t{self.contador_temp}"
        self.contador_temp += 1
        return nome

    def token_atual(self):
        """Retorna o token apontado pelo ponteiro atual ou None se chegou ao EOF."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consumir(self, tipo_esperado):
        """
        Valida o token corrente contra o tipo esperado.
        Se correto, avança o ponteiro; senão, gera um Erro Sintático descritivo.
        """
        token = self.token_atual()
        if token and token.tipo == tipo_esperado:
            self.pos += 1
            return token
        else:
            pos_erro = token.posicao if token else "fim da linha"
            valor_erro = token.valor if token else "EOF"
            raise Exception(f"Erro Sintático: Esperado '{tipo_esperado}', mas encontrado '{valor_erro}' na posição {pos_erro}.")

    def parse(self):
        """Função de entrada que inicia a análise gramatical pelo símbolo inicial E."""
        lugar_resultado, valor_calculado = self.parse_E()
        
        # Garante que após avaliar a expressão não restaram tokens perdidos na entrada
        if self.token_atual() is not None:
            raise Exception(f"Erro Sintático: Tokens extras inesperados a partir da posição {self.token_atual().posicao}.")
        
        return lugar_resultado, valor_calculado, self.instrucoes_c3e

    # -------------------------------------------------------------------------
    # Produções da Gramática Fatorada
    # -------------------------------------------------------------------------

    # Regra: E -> T E'
    # E é o símbolo inicial para expressões de soma (de menor precedência).
    def parse_E(self):
        lugar_esq, val_esq = self.parse_T()
        return self.parse_E_linha(lugar_esq, val_esq)

    # Regra: E' -> + T E' | epsilon
    # Permite recursividade à direita para operadores de adição (eliminando recursão à esquerda).
    def parse_E_linha(self, lugar_esq, val_esq):
        token = self.token_atual()
        if token and token.tipo == TOKEN_SOMA:
            self.consumir(TOKEN_SOMA)
            lugar_dir, val_dir = self.parse_T()
            
            # Geração de Código Intermediário (C3E)
            temp = self.novo_temporario()
            self.instrucoes_c3e.append(f"{temp} = {lugar_esq} + {lugar_dir}")
            
            # Semântica Sintetizada: soma os valores das subárvores e propaga recursivamente
            return self.parse_E_linha(temp, val_esq + val_dir)
        return lugar_esq, val_esq

    # Regra: T -> F T'
    # Representa termos matemáticos (operações de multiplicação, com precedência superior à soma).
    def parse_T(self):
        lugar_esq, val_esq = self.parse_F()
        return self.parse_T_linha(lugar_esq, val_esq)

    # Regra: T' -> * F T' | epsilon
    # Permite recursividade à direita para multiplicação.
    def parse_T_linha(self, lugar_esq, val_esq):
        token = self.token_atual()
        if token and token.tipo == TOKEN_MULT:
            self.consumir(TOKEN_MULT)
            lugar_dir, val_dir = self.parse_F()
            
            # Geração de Código Intermediário (C3E)
            temp = self.novo_temporario()
            self.instrucoes_c3e.append(f"{temp} = {lugar_esq} * {lugar_dir}")
            
            # Semântica Sintetizada: multiplica os valores e propaga o acumulado
            return self.parse_T_linha(temp, val_esq * val_dir)
        return lugar_esq, val_esq

    # Regra: F -> ( E ) | NUM
    # Fatores da expressão (máxima precedência): números literais ou expressões agrupadas entre parênteses.
    def parse_F(self):
        token = self.token_atual()
        if token and token.tipo == TOKEN_NUM:
            t_num = self.consumir(TOKEN_NUM)
            valor_numerico = float(t_num.valor)
            # Retorna o identificador textual (para o C3E) e o valor computado (para o interpretador)
            return t_num.valor, valor_numerico
        elif token and token.tipo == TOKEN_APAR:
            self.consumir(TOKEN_APAR)
            # Avalia a subexpressão inteira contida dentro dos parênteses
            lugar_interno, val_interno = self.parse_E()
            self.consumir(TOKEN_FPAR)
            return lugar_interno, val_interno
        else:
            pos_erro = token.posicao if token else "fim da linha"
            raise Exception(f"Erro Sintático: Esperado um número ou '(', mas encontrado erro na posição {pos_erro}.")

# =============================================================================
# 4. LOOP PRINCIPAL (REPL - READ-EVAL-PRINT LOOP)
# =============================================================================
def executar_tradutor():
    """Gerencia a entrada do terminal, executa as camadas do compilador e exibe os resultados."""
    print("====================================================")
    print("Tradutor de Expressões")
    print("Suporta: Espaços, Múltiplos dígitos e Ponto Flutuante")
    print("====================================================")
    
    while True:
        try:
            entrada = input("\nDigite a expressão > ").strip()
            if entrada.lower() == 'sair':
                break
            if not entrada:
                continue

            # Passo 1: Executa a Análise Léxica
            lista_tokens = lexer(entrada)
            
            # Passo 2: Executa a Análise Sintática/Semântica e Geração C3E
            parser = Parser(lista_tokens)
            lugar_final, valor_final, codigo_gerado = parser.parse()
            
            # Formata a exibição do resultado (retira o '.0' caso seja um inteiro para visualização limpa)
            valor_exibido = int(valor_final) if valor_final.is_integer() else valor_final

            print("\nResultado Léxico e Sintático: CORRETO")
            print(f"Resultado Calculado: {valor_exibido}")
            print("----------------------------------------------------")
            print("CÓDIGO DE TRÊS ENDEREÇOS:")
            
            # Ordena as instruções para garantir que multiplicações sejam exibidas antes das somas no relatório final
            instrucoes_ordenadas = sorted(codigo_gerado, key=lambda x: '*' not in x)
            
            if not instrucoes_ordenadas:
                print(f"  t0 = {lugar_final}")
            else:
                for linha in instrucoes_ordenadas:
                    print(f"  {linha}")
            print("----------------------------------------------------")

        except Exception as erro:
            # Captura qualquer erro de sintaxe ou léxico emitido durante a execução e imprime no stderr
            print(erro, file=sys.stderr)

if __name__ == "__main__":
    executar_tradutor()
