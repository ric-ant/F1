# Guia de Uso

## Instalação

### Pré-requisitos

- [pyenv](https://github.com/pyenv/pyenv) para gerenciar a versão do Python
- [Poetry](https://python-poetry.org/) para dependências

```bash
# 1. Garantir Python 3.12
pyenv install 3.12.4
pyenv local 3.12.4

# 2. Configurar o Poetry para usar o Python do pyenv
poetry env use $(pyenv which python)

# 3. Instalar dependências
poetry install
```

## Uso do CLI

### Sintaxe

```bash
poetry run f1-dashboard --year ANO --gp NOME_GP --session TIPO_SESSAO [--output ARQUIVO.html]
```

### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `--year` | inteiro | sim | Ano do campeonato (ex.: `2023`, `2024`) |
| `--gp` | string | sim | Nome do país ou cidade do GP (ex.: `Monaco`, `Brazil`, `Italy`) |
| `--session` | string | sim | Tipo de sessão: `Race`, `Qualifying`, `Sprint`, `Practice 1`, etc. |
| `--output` | string | não | Nome do arquivo HTML de saída (padrão: `dashboard.html`) |

### Exemplos

```bash
# GP de Mônaco 2023 — Corrida
poetry run f1-dashboard --year 2023 --gp Monaco --session Race

# GP do Brasil 2023 — Qualificação, com nome customizado
poetry run f1-dashboard --year 2023 --gp Brazil --session Qualifying --output brazil_quali_2023.html

# GP da Itália 2024 — Corrida
poetry run f1-dashboard --year 2024 --gp Italy --session Race --output monza_2024.html
```

## Interpretando o Dashboard

### Gráfico de Comparativo de Voltas

- **Eixo X:** número da volta
- **Eixo Y:** tempo da volta em segundos
- **Cada linha:** um piloto (identificado pelo acrônimo no hover)
- **Hover:** exibe nome do piloto, número da volta, tempo total e tempos por setor (S1, S2, S3)
- **Voltas ausentes:** pit stops e voltas de entrada/saída do pit são omitidos do gráfico (sem `lap_duration`)

### Tabela de Pit Stops

Abaixo do gráfico, uma tabela HTML lista todos os pit stops da sessão com:

- Número do piloto
- Volta em que parou
- Duração da parada no box (em segundos)

## Limites da API

A API OpenF1 possui rate limiting no tier gratuito (3 req/s, 30/min). Para sessões com muitos pilotos e voltas, o tempo de download pode variar de alguns segundos a poucos minutos. O cliente respeita automaticamente esses limites com retry em caso de erro 429.
