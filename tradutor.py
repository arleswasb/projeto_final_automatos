import re
import sys

# -----------------------------------------------------------------------------
# 1. DEFINIÇÃO DOS TOKENS
# -----------------------------------------------------------------------------
TOKEN_NUM   = 'NUM'    
TOKEN_SOMA  = 'SOMA'
TOKEN_MULT  = 'MULT'
TOKEN_APAR  = 'APAR'
TOKEN_FPAR  = 'FPAR'

class Token:
    def __init__(self, tipo, valor, posicao):
        self.tipo = tipo
        self.valor = valor
        self.posicao = posicao

    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}')"

# -----------------------------------------------------------------------------
# 2. ANALISADOR LÉXICO (LEXER)
# -----------------------------------------------------------------------------
def lexer(codigo_fonte):
    tokens = []
    i = 0
    tamanho = len(codigo_fonte)

    regex_num = re.compile(r'^[0-9]+(?:\.[0-9]+)?')
    regex_soma = re.compile(r'^\+')
    regex_mult = re.compile(r'^\*')
    regex_apar = re.compile(r'^\(')
    regex_fpar = re.compile(r'^\)')
    regex_espaco = re.compile(r'^\s+')

    while i < tamanho:
        sub_string = codigo_fonte[i:]

        match_espaco = regex_espaco.match(sub_string)
        if match_espaco:
            i += len(match_espaco.group(0))
            continue

        match_num = regex_num.match(sub_string)
        if match_num:
            valor = match_num.group(0)
            tokens.append(Token(TOKEN_NUM, valor, i))
            i += len(valor)
            continue

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

        raise Exception(f"Erro Léxico: Caractere inválido '{codigo_fonte[i]}' na posição {i}.")

    return tokens

# -----------------------------------------------------------------------------
# 3. PARSER E GERADOR
# -----------------------------------------------------------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.contador_temp = 0
        self.instrucoes_c3e = []

    def novo_temporario(self):
        nome = f"t{self.contador_temp}"
        self.contador_temp += 1
        return nome

    def token_atual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consumir(self, tipo_esperado):
        token = self.token_atual()
        if token and token.tipo == tipo_esperado:
            self.pos += 1
            return token
        else:
            pos_erro = token.posicao if token else "fim da linha"
            valor_erro = token.valor if token else "EOF"
            raise Exception(f"Erro Sintático: Esperado '{tipo_esperado}', mas encontrado '{valor_erro}' na posição {pos_erro}.")

    def parse(self):
        lugar_resultado, valor_calculado = self.parse_E()
        
        if self.token_atual() is not None:
            raise Exception(f"Erro Sintático: Tokens extras inesperados a partir da posição {self.token_atual().posicao}.")
        
        return lugar_resultado, valor_calculado, self.instrucoes_c3e

    # E -> T E'
    def parse_E(self):
        lugar_esq, val_esq = self.parse_T()
        return self.parse_E_linha(lugar_esq, val_esq)

    # E' -> + T E' | epsilon
    def parse_E_linha(self, lugar_esq, val_esq):
        token = self.token_atual()
        if token and token.tipo == TOKEN_SOMA:
            self.consumir(TOKEN_SOMA)
            lugar_dir, val_dir = self.parse_T()
            
            temp = self.novo_temporario()
            self.instrucoes_c3e.append(f"{temp} = {lugar_esq} + {lugar_dir}")
            
            return self.parse_E_linha(temp, val_esq + val_dir)
        return lugar_esq, val_esq

    # T -> F T'
    def parse_T(self):
        lugar_esq, val_esq = self.parse_F()
        return self.parse_T_linha(lugar_esq, val_esq)

    # T' -> * F T' | epsilon
    def parse_T_linha(self, lugar_esq, val_esq):
        token = self.token_atual()
        if token and token.tipo == TOKEN_MULT:
            self.consumir(TOKEN_MULT)
            lugar_dir, val_dir = self.parse_F()
            
            temp = self.novo_temporario()
            self.instrucoes_c3e.append(f"{temp} = {lugar_esq} * {lugar_dir}")
            
            return self.parse_T_linha(temp, val_esq * val_dir)
        return lugar_esq, val_esq

    # F -> ( E ) | id
    def parse_F(self):
        token = self.token_atual()
        if token and token.tipo == TOKEN_NUM:
            t_num = self.consumir(TOKEN_NUM)
            valor_numerico = float(t_num.valor)
            return t_num.valor, valor_numerico
        elif token and token.tipo == TOKEN_APAR:
            self.consumir(TOKEN_APAR)
            # CORREÇÃO: parse_E() retorna 2 valores (lugar, valor). Capturamos apenas os 2 de forma correta!
            lugar_interno, val_interno = self.parse_E()
            self.consumir(TOKEN_FPAR)
            return lugar_interno, val_interno
        else:
            pos_erro = token.posicao if token else "fim da linha"
            raise Exception(f"Erro Sintático: Esperado um número ou '(', mas encontrado erro na posição {pos_erro}.")

# -----------------------------------------------------------------------------
# 4. LOOP PRINCIPAL (REPL)
# -----------------------------------------------------------------------------
def executar_tradutor():
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

            lista_tokens = lexer(entrada)
            parser = Parser(lista_tokens)
            lugar_final, valor_final, codigo_gerado = parser.parse()
            
            # Formata a exibição do resultado (remove o .0 desnecessário se for inteiro)
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
            print(erro, file=sys.stderr)

if __name__ == "__main__":
    executar_tradutor()
