# ufabc-cv

Notebooks, scripts e relatórios da disciplina de Visão Computacional (UFABC).

Site publicado: <https://kaykyb.github.io/ufabc-cv/>

## Estrutura

```
laboratorios/        # notebooks Jupyter, um diretório por laboratório (lab1 ... lab6)
  labN/labN.ipynb    # notebook do laboratório
  labN/data/         # dados do laboratório (amostras pequenas; grandes ficam fora do git)
trabalho-final/      # projeto final: scripts Python, modelo e notebook de análise
  *.py               # captura, detecção, localização e treino
  analise_resultados.ipynb
  resources/         # dados de apoio (enquete de opinião, questões)
private/             # material de apoio não publicado (entrevistas, manual)
site/                # site Hugo (tema PaperMod)
  content/posts/     # relatórios - um page bundle por laboratório/etapa
  layouts/           # overrides de template
  hugo.toml          # configuração do site
```

## Fluxo de um relatório

1. Desenvolver o notebook em `laboratorios/labN/labN.ipynb`.
2. Criar `site/content/posts/labN/index.md`.
3. Exportar figuras relevantes para o mesmo diretório do `index.md` e referenciá-las como `![](figura.png)`.
4. Incluir no topo do post o link para o notebook no GitHub.

Os relatórios são escritos à mão (prosa, blocos de código, imagens). Não há conversão automática de `.ipynb`.

## Desenvolvimento local

```
make serve     # hugo server em http://localhost:1313
make build     # gera site/public
make clean
```

Clonar com submódulos: `git clone --recurse-submodules ...` (o tema PaperMod é um submódulo).

## Deploy

GitHub Actions (`.github/workflows/deploy.yml`) faz build e publica no GitHub Pages a cada push em `main`. Em **Settings → Pages**, definir _Source_ como **GitHub Actions**.