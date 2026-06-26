---
title: "[1] Trabalho Final - Tema"
authors:
  [
    "Kayky de Brito dos Santos",
    "Andre Marques da Silva",
    "Rafael de Souza Coelho",
  ]
date: 2026-06-26
summary: "Definição do tema do trabalho final: um programa de reconhecimento de valores de cédulas em tempo real, voltado a pessoas com baixa visão no comércio de bairro."
tags: ["trabalho"]
---

**Equipe:** Sem Título

**Integrantes:**

- Kayky de Brito dos Santos
- André Marques da Silva
- Rafael de Souza Coelho

**Data de publicação:** 26 de junho de 2026

**Título do trabalho:** Programa de Reconhecimento de Valores de Cédulas

## 1. Introdução

Este documento corresponde ao segundo entregável do trabalho final da disciplina (a **definição do tema**) e tem como base a fase de empatia registrada no relatório de [entrevistas empáticas]({{< ref "trabalho-entrevistas" >}}). A partir das dores levantadas nas entrevistas, a equipe definiu como tema o desenvolvimento de um **sistema de visão computacional em tempo real capaz de reconhecer o valor de cédulas do Real (R$)** e informá-lo ao usuário por meio de áudio.

A escolha une os dois pilares exigidos pelo manual: o **rigor matemático** da calibração de câmera e a **aplicabilidade prática** de uma rede neural convolucional treinada para um problema específico e bem delimitado, em linha com a recomendação de que "menos é mais, desde que seja preciso".

## 2. Contexto e Cenário de Aplicação

O cenário de aplicação é o **comércio de bairro** atendido por pessoas com **baixa visão**, situação muito comum entre comerciantes mais velhos. Nesse contexto, a conferência de cédulas no caixa é uma tarefa cotidiana, repetitiva e crítica: um erro de leitura significa troco errado, prejuízo financeiro e exposição a fraudes.

O sistema proposto funciona com uma webcam apontada para a área do caixa. Ao aproximar uma cédula, o programa classifica sua denominação (R$ 2, 5, 10, 20, 50, 100 e 200) e anuncia o valor em voz alta, dispensando a leitura visual e a dependência de terceiros.

### 2.1. Síntese das entrevistas empáticas

As entrevistas que fundamentam o tema estão detalhadas no [relatório da fase de empatia]({{< ref "trabalho-entrevistas" >}}). Em resumo:

- **Dona Marlene (61 anos, comerciante com catarata inicial):** não distingue denominações com segurança sob luz fraca ou com cédulas amassadas, confunde com frequência as notas de R$ 50 e R$ 100 e já recebeu cédulas trocadas de má fé. Como não enxerga para enquadrar a nota, exige uma interação simples, de "só encostar".
- **Kauã (19 anos, auxiliar de caixa):** hoje supre manualmente a limitação visual da mãe conferindo o dinheiro e o troco. Aponta como essenciais a **simplicidade**, a **confiabilidade** e o funcionamento com **cédulas desgastadas**, que são as que mais circulam no comércio.

Esses relatos definem três requisitos centrais do sistema: tolerância a imagens mal alinhadas (calibração), robustez a cédulas em condições variadas (rede neural treinada com diversidade) e saída acessível (áudio).

## 3. Justificativa e Motivação

Segundo o IBGE, milhões de brasileiros convivem com algum grau de deficiência visual, e parcela expressiva atua ou depende do comércio informal. A perda de acuidade associada ao envelhecimento (catarata, baixa visão) compromete justamente a tarefa de distinguir cédulas, que perderam, ao longo das últimas famílias do Real, parte das diferenças de tamanho que antes permitiam o reconhecimento pelo tato.

A motivação é, portanto, **devolver autonomia** a esse público: reduzir erros de troco, diminuir a exposição a fraudes e eliminar o constrangimento de pedir a confirmação do valor a um terceiro ou ao próprio cliente. Trata-se de um problema real, recorrente e com impacto financeiro direto sobre pequenos comerciantes.

## 4. Originalidade

Existem soluções comerciais e assistivas que tangenciam o problema, o que confirma sua relevância, mas também deixa espaço para a proposta:

- **Aplicativos de celular** como o _Cash Reader_ e o modo de identificação de dinheiro do _Seeing AI_ (Microsoft) reconhecem cédulas pela câmera do smartphone. Exigem, porém, que o usuário segure o aparelho e enquadre a nota, o que é inviável para quem está com as mãos ocupadas no caixa e não enxerga para mirar.
- **Serviços de assistência humana** como o _Be My Eyes_ dependem de um voluntário remoto, com latência e necessidade de conexão.
- **Marcações táteis** das próprias cédulas e réguas de identificação ajudam, mas falham com notas amassadas ou desgastadas.

A originalidade da nossa proposta está em ser um sistema **fixo no ponto de venda**, operado por aproximação (sem necessidade de mirar), **robusto a cédulas desgastadas e a enquadramentos ruins** graças à calibração obrigatória, e com **retorno sonoro imediato**, desenhado especificamente para a rotina do comerciante com baixa visão.

## 5. Requisitos Técnicos

O tema atende integralmente aos requisitos obrigatórios do manual:

- **Calibração de câmera (mandatório):** como a usuária não consegue alinhar a cédula, a entrada é ruidosa e mal enquadrada. O sistema, em Python com OpenCV, fará a calibração por padrão xadrez (_chessboard_), extraindo parâmetros intrínsecos e extrínsecos, corrigindo distorções radiais e tangenciais e demonstrando o **erro de reprojeção**.
- **Funcionalidade principal — Deep Learning (CNNs):** uma rede neural convolucional treinada e adaptada para **classificar a denominação** da cédula a partir do quadro corrigido, com dados em condições variadas (iluminação, desgaste, ângulo) para garantir robustez.
- **Saída acessível (TTS):** a denominação classificada é convertida em **áudio** por síntese de voz, anunciando o valor ao usuário.

## 6. Análise de Desempenho (prevista)

Para comprovar a robustez, conforme o manual, a equipe coletará:

- **Latência / FPS** durante a execução em tempo real;
- **Matriz de confusão** com precisão, revocação e F1-score por denominação;
- **Erro de reprojeção** (em pixels) como validação da calibração.

## 7. Benefícios Esperados

- **Autonomia** ao comerciante com baixa visão, sem depender de terceiros para conferir cédulas.
- **Redução de prejuízos** por troco errado e por fraudes com notas trocadas.
- **Simplicidade de uso**, com interação por aproximação e resposta em voz alta.
- **Baixo custo**, por utilizar webcam comum e software livre (Python e OpenCV).

## 8. Referências

- LearnOpenCV. _Camera Calibration using OpenCV_. Disponível em: <https://learnopencv.com/camera-calibration-using-opencv/>.
- LearnOpenCV. _Understanding Lens Distortion_. Disponível em: <https://learnopencv.com/understanding-lens-distortion/>.
- LearnOpenCV. _Geometry of Image Formation_. Disponível em: <https://learnopencv.com/geometry-of-image-formation/>.
- LearnOpenCV. _Image Classification using Convolutional Neural Networks_. Disponível em: <https://learnopencv.com/image-classification-using-convolutional-neural-networks-in-keras/>.
- Banco Central do Brasil. _Segunda família do Real: características das cédulas_.
- Microsoft. _Seeing AI_ (modo de identificação de dinheiro). Cash Reader. Be My Eyes.
