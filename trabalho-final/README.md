# Programa de Reconhecimento de Valores de Cédulas

Manual de uso do software do trabalho final da disciplina de Visão Computacional (UFABC).

**Equipe Sem Título:** Kayky de Brito dos Santos, André Marques da Silva e Rafael de Souza Coelho.

O sistema reconhece a denominação de cédulas do Real em tempo real, a partir de uma câmera fixa apontada para uma bancada preta. O ciclo completo tem três passos: **capturar** o dataset, **treinar** o modelo e **detectar** ao vivo.

## Arquivos

| Arquivo | Função |
| --- | --- |
| `capturar.py` | Ferramenta interativa de captura de imagens para o dataset |
| `localizacao.py` | Localização da cédula por visão clássica (Otsu + contornos) |
| `treinar.py` | Treino da CNN sobre o dataset capturado |
| `detectar.py` | Detecção ao vivo no feed da câmera, com anúncio do valor por voz |
| `modelo.pt` | Modelo treinado (pesos + classes + tamanho de entrada) |
| `requirements.txt` | Dependências Python |
| `dataset/` | Imagens capturadas, uma pasta por classe (não versionada) |

## Requisitos e instalação

- Python 3.10 ou superior
- Webcam USB (o padrão dos scripts procura a câmera "WC056" no macOS; use `--camera N` em outros sistemas)
- macOS, Linux ou Windows (a seleção de câmera por nome só funciona no macOS)

```bash
pip install -r requirements.txt
```

Instala OpenCV, NumPy, PyTorch, Torchvision e Pillow.

## Montagem física

Antes de usar o software, monte a maquete:

1. Forre a bancada com um fundo **preto fosco** (a localização da nota depende do fundo escuro e uniforme).
2. Fixe a câmera acima da bancada, apontada para baixo, cobrindo a área central. Qualquer suporte estável serve; na montagem da equipe usamos um suporte de headphone com um extensor de palitos de sorvete no topo segurando a câmera, e uma pilha atrás como contrapeso.
3. Ilumine a cena de forma estável; evite luz direta que crie reflexos na cédula.
4. Conecte a câmera ao computador antes de rodar os scripts.

## Passo 1: capturar o dataset (`capturar.py`)

```bash
python capturar.py                 # câmera WC056, classe inicial nota_50
python capturar.py --classe vazio  # começa capturando o fundo vazio
python capturar.py --camera 1      # força um índice de câmera específico
```

Abre uma janela com o feed da câmera e um HUD mostrando a classe ativa, o contador de imagens salvas e uma guia verde de enquadramento (60% x 70% do quadro, apenas visual).

### Teclas

| Tecla | Ação |
| --- | --- |
| `ESPAÇO` | Salva o frame atual na classe ativa (sem o HUD) |
| `1` a `8` | Troca a classe ativa: vazio, nota_2, nota_5, nota_10, nota_20, nota_50, nota_100, nota_200 |
| `u` | Desfaz (apaga o último arquivo salvo) |
| `g` | Liga/desliga a guia de enquadramento |
| `q` / `ESC` | Sai |

As imagens vão para `dataset/<classe>/` com nome único por timestamp. Fluxo típico de uma sessão: posicionar a nota na área da guia, salvar com `ESPAÇO`, girar/mover/virar a nota entre um salvamento e outro, trocar de classe com as teclas numéricas e repetir. Capture também a classe `vazio` (bancada sem nota) para o sistema saber reconhecer a ausência de cédula.

### Opções úteis

| Flag | Efeito |
| --- | --- |
| `--saida PASTA` | Muda a pasta raiz do dataset (padrão: `dataset`) |
| `--largura N --altura N` | Força a resolução do frame (padrão: resolução nativa) |
| `--travar` | Tenta desligar auto-exposição e auto-white-balance |
| `--exposicao V` | Exposição manual (implica `--travar`) |
| `--wb-temp K` | Temperatura do white balance em Kelvin (implica `--travar`) |

Atenção: no macOS (AVFoundation) muitas câmeras ignoram o travamento via OpenCV. O script imprime os valores lidos de volta; se não mudaram, trave por fora (app "Webcam Settings" ou `uvc-util`) ou fixe a iluminação da cena.

## Passo 2: treinar o modelo (`treinar.py`)

```bash
python treinar.py                 # padrões: 25 épocas, batch 32, entrada 192x192
python treinar.py --epocas 30     # treina por mais tempo
python treinar.py --tamanho 160   # entrada menor (mais rápido)
```

O script lê `dataset/<classe>/`, separa 20% para validação (split reprodutível, semente 42), aplica data augmentation apenas no treino e salva o melhor modelo (maior acurácia de validação) em `modelo.pt`. O progresso é impresso época a época.

O dispositivo é escolhido automaticamente: GPU da Apple (MPS) se houver, senão CUDA, senão CPU.

| Flag | Efeito |
| --- | --- |
| `--dataset PASTA` | Pasta raiz do dataset (padrão: `dataset`) |
| `--saida-modelo ARQ` | Arquivo de saída (padrão: `modelo.pt`) |
| `--epocas N` | Número de épocas (padrão: 25) |
| `--batch N` | Tamanho do batch (padrão: 32) |
| `--lr V` | Taxa de aprendizado (padrão: 1e-3) |
| `--tamanho N` | Lado da imagem de entrada (padrão: 192) |
| `--val-split F` | Fração para validação (padrão: 0.2) |
| `--seed N` | Semente (padrão: 42) |

## Passo 3: detecção ao vivo (`detectar.py`)

```bash
python detectar.py                 # câmera WC056, modelo.pt, limiar 0.8
python detectar.py --limiar 0.9    # exige mais confiança para acusar detecção
python detectar.py --sem-voz       # desliga o anúncio falado
```

A cada quadro o sistema recorta a nota (mesma localização clássica do treino), classifica o recorte e mostra a previsão com a confiança. Quando a classe prevista é uma cédula com confiança acima do limiar, a tela destaca "NOTA X DETECTADA", desenha a caixa rotacionada em volta da nota e **fala o valor em voz alta** ("cinquenta reais"). Bancada vazia responde "vazio" sem passar pela rede. `q` ou `ESC` encerra.

A fala tem debounce: a mesma nota só é repetida depois de 7 segundos (ajustável com `--debounce`), mas uma nota diferente é anunciada imediatamente. O TTS usa o comando `say` no macOS ou o `espeak` em outros sistemas; se nenhum dos dois existir, o programa avisa e segue só com a tela.

| Flag | Efeito |
| --- | --- |
| `--modelo ARQ` | Arquivo do modelo treinado (padrão: `modelo.pt`) |
| `--limiar F` | Confiança mínima para acusar detecção, 0 a 1 (padrão: 0.8) |
| `--area-min F` | Área mínima da nota como fração do frame (padrão: 0.02) |
| `--debounce F` | Segundos até repetir a fala da mesma nota (padrão: 7) |
| `--sem-voz` | Desliga o anúncio falado |
| `--camera N` / `--nome-camera NOME` | Seleção da câmera, como na captura |

## Solução de problemas

- **"Nao consegui abrir a camera N":** liste/teste outros índices com `--camera 0`, `--camera 1`, etc. No macOS, confira o nome da câmera com `system_profiler SPCameraDataType`.
- **Detecção instável ou nota não encontrada:** verifique o fundo (precisa ser escuro e fosco) e a iluminação; ajuste `--area-min` se a nota ocupar uma fração muito pequena do quadro.
- **Modelo confunde denominações:** capture mais imagens das classes confundidas (frente e verso, rotações, posições variadas) e retreine.
- **Cores/brilho variando entre sessões:** tente `--travar` na captura; se a câmera ignorar, fixe a iluminação.
- **Sem anúncio falado:** no macOS o `say` já vem com o sistema; no Linux instale o `espeak`. Verifique também o volume e se a detecção está de fato acontecendo (a fala só ocorre com confiança acima do limiar). Para conferir sem áudio, use a tela; para silenciar de propósito, use `--sem-voz`.
