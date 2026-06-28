

# Tradutor de Expressões Aritméticas (Compilador Front-End)

Este repositório contém a implementação completa de um **Tradutor e Interpretador de Expressões Aritméticas**, desenvolvido como requisito avaliativo para o Trabalho Final da disciplina **Autômatos e Linguagens Formais (DCA-3705)**, ministrada pelo **Prof. Luiz Affonso Guedes** na Universidade Federal do Rio Grande do Norte (UFRN).

O software contempla todas as subetapas fundamentais do *front-end* de um compilador: **Análise Léxica**, **Análise Sintática**, **Análise Semântica/Interpretador** e **Geração de Código Intermediário** (Código de Três Endereços - C3E).

---

## Funcionalidades Atendidas

O compilador opera em modo REPL (*Read-Eval-Print Loop*), aceitando entradas contínuas e avaliando-as em tempo real com os seguintes suportes:
- **Análise Léxica via RegEx:** Mapeamento eficiente e preciso de tokens em conformidade com as regras aritméticas formais.
- **Ignorância de Espaços Transparentes:** Aceitação de qualquer quantidade de espaços em branco inseridos arbitrariamente no meio da expressão.
- **Suporte a Múltiplos Dígitos:** Leitura unificada de dezenas, centenas e milhares como tokens numéricos individuais.
- **Suporte a Ponto Flutuante:** Capacidade de analisar e calcular expressões utilizando decimais separados por ponto.
- **Análise Sintática Preditiva LL(1):** Execução orientada por Parser Descendente Recursivo estável e sem necessidade de retrocesso (*backtracking*).
- **Tratamento Preciso de Erros:** Identificação de falhas sintáticas ou léxicas apontando o caractere faltante/incorrecto e seu índice de localização exato.
- **Geração de Código de Três Endereços (C3E):** Linearização matemática sequencial em variáveis temporárias (`t0, t1`), preservando a prioridade dos parênteses e operadores.

---

## Especificação da Gramática Livre de Contexto (GLC)

A gramática padrão de expressões aritméticas foi tratada e adaptada para remover a ambiguidade e eliminar a recursão à esquerda, permitindo o correto processamento por um algoritmo de parser LL(1).

### 1. Forma Padrão (Ambiguidade e Recursão à Esquerda)
$$E \rightarrow E + T \mid T$$
$$T \rightarrow T * F \mid F$$
$$F \rightarrow ( E ) \mid id$$

### 2. Forma Fatorada Normalizada (Implementada no Código)
* Onde **&epsilon;** representa a palavra vazia (Epsilon) e **NUM** representa o Token identificador de números inteiros não negativos e decimais.
```text
E  -> T E'
E' -> + T E' | ε
T  -> F T'
T' -> * F T' | ε
F  -> ( E ) | NUM

```

---

## Arquitetura do Sistema

O arquivo principal [`tradutor.py`](file:///c:/Users/Administrador/OneDrive/Documentos/GitHub/projeto_final_automatos/tradutor.py) divide-se logicamente em 4 camadas estruturais distintas:

| Módulo | Tipo | Descrição Técnica |
| --- | --- | --- |
| **Analisador Léxico (Lexer)** | `Definido via RegEx` | Escaneia a entrada caractere por caractere aplicando padrões regulares, encapsulando os tokens válidos em objetos contendo `tipo`, `valor` e `posicao`. |
| **Analisador Sintático (Parser)** | `Algoritmo LL(1)` | Implementa as funções recursivas associadas às regras fatoradas (`parse_E`, `parse_E_linha`, `parse_T`, etc.), validando a integridade estrutural. |
| **Interpretador Semântico** | `Sintetizado` | Executa os cálculos matemáticos em tempo de redução sintática através da propagação ordenada dos atributos numéricos de baixo para cima. |
| **Gerador de Código (C3E)** | `Código Intermediário` | Aloca registradores virtuais (`t0`, `t1`, ...) para as operações verdadeiras e formata as instruções legíveis ordenadas logicamente. |

### Funcionamento Detalhado das Camadas

#### 1. Analisador Léxico (Lexer)
O papel do Lexer é ler a string de entrada caractere por caractere e agrupá-los em unidades significativas chamadas **Tokens** (`TOKEN_NUM`, `TOKEN_SOMA`, `TOKEN_MULT`, `TOKEN_APAR`, `TOKEN_FPAR`). 
- **Mapeamento via RegEx:** Utiliza expressões regulares (RegEx) compiladas para casar os padrões a partir da posição atual da string (`sub_string = codigo_fonte[i:]`).
- **Números e Decimais:** A RegEx `r'^[0-9]+(?:\.[0-9]+)?'` garante suporte completo a números inteiros com múltiplos dígitos e pontos flutuantes.
- **Espaços em branco:** A RegEx `r'^\s+'` consome os espaços transparentes e incrementa o índice de busca sem gerar tokens.
- **Tratamento de Erros:** Caso um caractere não case com nenhum dos padrões válidos, uma exceção léxica é levantada, detalhando o caractere e a posição exata.

#### 2. Analisador Sintático (Parser LL(1))
O Parser valida se os tokens gerados pelo Lexer seguem uma estrutura sintática correta baseada na gramática de expressões aritméticas livre de contexto.
- **Parser Descendente Recursivo:** Cada regra fatorada da GLC corresponde a uma função recursiva (ex: `parse_E()`, `parse_E_linha()`, `parse_T()`, `parse_T_linha()`, `parse_F()`).
- **Consumo de Tokens:** O método `consumir(tipo_esperado)` valida o token atual e avança o ponteiro de leitura. Se houver desvio das regras gramaticais, o compilador gera um erro apontando o que era esperado e o token inválido encontrado.

#### 3. Interpretador Semântico
O cálculo do resultado matemático é avaliado de forma **sintetizada** (ou seja, propagado de baixo para cima na árvore de sintaxe):
- O nível base (`parse_F`) lê o token do número e retorna seu valor real correspondente (convertido via `float()`).
- Os níveis intermediários de precedência (`parse_T` e `parse_T_linha` para multiplicações, e depois `parse_E` e `parse_E_linha` para somas) combinam recursivamente os valores recebidos e propagam os resultados acumulados para cima até a raiz.

#### 4. Gerador de Código Intermediário (C3E)
O Parser também atua gerando o código de três endereços (C3E) durante as reduções sintáticas:
- Sempre que uma operação é realizada, gera-se um registrador temporário exclusivo via `novo_temporario()` (ex: `t0`, `t1`).
- A linha de instrução correspondente é adicionada em `instrucoes_c3e` (ex: `t0 = 2 + 3`).
- A variável temporária passa a representar aquele valor para as operações de níveis superiores na árvore sintática, permitindo a linearização da expressão de forma organizada.

---

## Como Executar o Projeto

O projeto foi inteiramente codificado na linguagem **Python 3**, utilizando exclusivamente pacotes embarcados em sua biblioteca padrão. Nenhuma dependência externa se faz necessária.

1. Garanta que possui o Python instalado em seu computador (versão 3.6 ou superior).
2. Abra o terminal na pasta contendo o script do projeto.
3. Inicie o tradutor interativo executando:

```bash
python tradutor.py

```

4. Para encerrar o programa a qualquer momento, digite no terminal interativo:

```text
sair

```

---

## Exemplos Práticos de Interação

### Exemplo de Fluxo Válido (Com Precedência de Parênteses e Decimais)

```text
Digite a expressão > (2 + 3) * 4.5

Resultado Léxico e Sintático: CORRETO
Resultado Calculado: 22.5
----------------------------------------------------
CÓDIGO DE TRÊS ENDEREÇOS:
  t0 = 2 + 3
  t1 = t0 * 4.5
----------------------------------------------------

```

### Exemplo de Fluxo com Erro Sintático Detectado

```text
Digite a expressão > (+ 3 ) * 4
Erro Sintático: Esperado um número ou '(', mas encontrado erro na posição 1.

```
