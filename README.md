

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

O arquivo principal `tradutor.py` divide-se logicamente em 4 camadas estruturais distintas:

| Módulo | Tipo | Descrição Técnica |
| --- | --- | --- |
| **Analisador Léxico (Lexer)** | `Definido via RegEx` | Escaneia a entrada caractere por caractere aplicando padrões regulares, encapsulando os tokens válidos em objetos contendo `tipo`, `valor` e `posicao`. |
| **Analisador Sintático (Parser)** | `Algoritmo LL(1)` | Implementa as funções recursivas associadas às regras fatoradas (`parse_E`, `parse_E_linha`, `parse_T`, etc.), validando a integridade estrutural. |
| **Interpretador Semântico** | `Sintetizado` | Executa os cálculos matemáticos em tempo de redução sintática através da propagação ordenada dos atributos numéricos de baixo para cima. |
| **Gerador de Código (C3E)** | `Código Intermediário` | Aloca registradores virtuais (`t0`, `t1`, ...) para as operações verdadeiras e formata as instruções legíveis ordenadas logicamente. |

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
