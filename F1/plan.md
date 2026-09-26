# Implementation Plan — F1 Lap Comparison Dashboard

## Problem Statement

Construir um dashboard HTML interativo que consome a API OpenF1 (dados históricos) e exibe um comparativo de tempos de volta entre pilotos de uma sessão configurável pelo usuário, seguindo rigorosamente os padrões do SKILL.md (Poetry, Ruff, pytest/pytest-cov ≥ 50%, MkDocs Material).

## Requirements

- **Entrada:** usuário informa ano, nome do GP e tipo de sessão (ex.: `Race`, `Qualifying`)
- **Saída:** arquivo `dashboard.html` com gráficos interativos de comparativo de volta a volta
- **Dados consumidos:** `/sessions`, `/drivers`, `/laps` (core); `/stints` e `/pit` como contexto adicional
- **Sem autenticação:** apenas endpoints de dados históricos gratuitos
- **Stack:** Python 3.12, Poetry, Plotly (HTML interativo), Ruff, pytest, MkDocs Material
- **Qualidade:** cobertura ≥ 50%, lint sem erros, docs buildável com `--strict`

## Background

- A API OpenF1 tem base URL `https://api.openf1.org/v1/` e retorna JSON
- Rate limit: 3 req/s e 30/min no tier gratuito — o cliente precisa respeitar isso
- O fluxo natural de consulta é: `meetings` → `sessions` → `drivers` + `laps`
- `session_key` e `driver_number` são as chaves que unem todos os endpoints relevantes
- Plotly gera HTML standalone (`fig.write_html()`), zero dependência de servidor
- O projeto já tem estrutura base: `src/f1/`, `tests/`, `pyproject.toml` com Poetry
- Projeto localizado em: `c:\Users\USUARIO\projetos\projeto_F1\F1\`
- Pacote Python: `f1`, localizado em `src/f1/`
- SKILL.md em: `src/f1/SKILL.md`

## Proposed Solution

Estrutura em camadas dentro de `src/f1/`:

```
src/f1/
├── __init__.py
├── client.py        # HTTP client: busca dados da API com retry/rate-limit
├── models.py        # dataclasses tipadas: Session, Driver, Lap, Stint, Pit
├── fetcher.py       # orquestra as chamadas: resolve meeting → session → dados
├── report.py        # monta o dashboard HTML via Plotly
└── cli.py           # entrypoint: aceita argumentos (ano, gp, sessão)
```

Fluxo de execução:
- Usuário (ano + GP + sessão) → cli.py → fetcher.py → client.py → OpenF1 API → models.py → fetcher.py → report.py → dashboard.html

## Task Breakdown

### Task 1: Configurar o ambiente e dependências do projeto

- **Objetivo:** deixar o `pyproject.toml` completo com todas as dependências e configurações de ferramentas, e validar que o ambiente está funcional.
- **Implementação:**
  - Adicionar dependências de produção: `requests`, `plotly`
  - Adicionar dependências de dev: `ruff`, `pytest`, `pytest-cov`, `mkdocs-material`
  - Configurar seções `[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.coverage]` no `pyproject.toml`
  - Criar estrutura de docs: `docs/index.md`, `mkdocs.yml`
  - Criar `.gitignore` cobrindo `.venv/`, `site/`, `htmlcov/`, `__pycache__/`
  - Criar `tests/__init__.py` se não existir
- **Testes:** rodar `poetry run ruff check src tests` e `poetry run pytest` (suíte vazia deve passar)
- **Demo:** `poetry run mkdocs build --strict` conclui sem erros; `poetry run pytest` passa com 0 testes coletados.

### Task 2: Implementar o cliente HTTP (`client.py`) com testes

- **Objetivo:** criar um cliente robusto que faz GET na API OpenF1, respeita o rate limit e retorna JSON parseado.
- **Implementação:**
  - Classe `OpenF1Client` com método `get(endpoint, params)` que retorna `list[dict]`
  - URL base configurável via parâmetro (padrão: `https://api.openf1.org/v1/`, facilita testes com mock)
  - Timeout configurável (padrão 10s)
  - Retry simples em caso de 429 (rate limit): aguarda 1s e tenta novamente (máx 3 tentativas)
  - Levantar `requests.HTTPError` para outros erros HTTP
- **Testes** (`tests/test_client.py`):
  - Mock de `requests.get` com `pytest` + `unittest.mock`
  - Testar resposta bem-sucedida retornando lista de dicts
  - Testar status 429 com retry (verifica que tenta novamente)
  - Testar status 500 levantando exceção
  - Testar timeout
- **Demo:** `poetry run pytest tests/test_client.py` passa; cobertura de `client.py` ≥ 80%.

### Task 3: Definir os modelos de dados (`models.py`) com testes

- **Objetivo:** criar dataclasses tipadas que representam as entidades retornadas pela API.
- **Implementação:**
  - `Session(session_key: int, session_name: str, date_start: str, country_name: str)` com `from_dict`
  - `Driver(driver_number: int, full_name: str, team_name: str, name_acronym: str)` com `from_dict`
  - `Lap(driver_number: int, lap_number: int, lap_duration: float | None, duration_sector_1: float | None, duration_sector_2: float | None, duration_sector_3: float | None)` com `from_dict`
  - `Stint(driver_number: int, lap_start: int, lap_end: int, compound: str, tyre_age_at_start: int)` com `from_dict`
  - `Pit(driver_number: int, lap_number: int, pit_duration: float | None)` com `from_dict`
  - Todos os campos ausentes no dict resultam em `None` (sem levantar exceção)
- **Testes** (`tests/test_models.py`):
  - Testar `from_dict` com dicts completos para cada modelo
  - Testar `from_dict` com campos ausentes (deve resultar em `None`, não exceção)
- **Demo:** `poetry run pytest tests/test_models.py` passa; modelos importáveis diretamente de `f1`.

### Task 4: Implementar o fetcher de dados (`fetcher.py`) com testes

- **Objetivo:** orquestrar as chamadas à API para resolver o fluxo `meeting → session → drivers + laps`.
- **Implementação:**
  - `resolve_session(client, year: int, country_name: str, session_name: str) -> Session` — busca `/meetings` filtrado por `year` e `country_name`, depois `/sessions` filtrado por `meeting_key` e `session_name`, retorna o primeiro resultado como `Session`
  - `fetch_drivers(client, session_key: int) -> list[Driver]`
  - `fetch_laps(client, session_key: int) -> list[Lap]`
  - `fetch_stints(client, session_key: int) -> list[Stint]`
  - `fetch_pits(client, session_key: int) -> list[Pit]`
  - Levantar `ValueError` com mensagem clara se meeting ou sessão não for encontrado
- **Testes** (`tests/test_fetcher.py`):
  - Usar `OpenF1Client` mockado (ou mock direto do método `get`)
  - Testar `resolve_session` com dados válidos → retorna `Session` correta
  - Testar `resolve_session` quando meeting não encontrado → `ValueError`
  - Testar `resolve_session` quando sessão não encontrada → `ValueError`
  - Testar `fetch_laps`, `fetch_drivers` com dados mockados
- **Demo:** `poetry run pytest tests/test_fetcher.py` passa; cobertura do fetcher ≥ 60%.

### Task 5: Implementar o gerador de relatório HTML (`report.py`) com testes

- **Objetivo:** receber os dados processados e gerar um `dashboard.html` com gráfico interativo de comparativo de voltas.
- **Implementação:**
  - `build_lap_comparison_chart(laps: list[Lap], drivers: list[Driver]) -> go.Figure` — gráfico de linha usando `plotly.graph_objects`: eixo X = nº da volta, eixo Y = tempo da volta em segundos, uma linha por piloto (cor diferente), hover mostrando setor 1/2/3; voltas com `lap_duration=None` são ignoradas
  - `generate_dashboard(session: Session, laps: list[Lap], drivers: list[Driver], stints: list[Stint], pits: list[Pit], output_path: str = "dashboard.html") -> None` — monta o HTML com: título `{session.country_name} {session.session_name}`, o gráfico de comparativo de voltas, e uma tabela HTML simples de resumo de pit stops; usa `fig.write_html(output_path, include_plotlyjs="cdn")`
- **Testes** (`tests/test_report.py`):
  - Criar dados sintéticos (2 pilotos, 5 voltas cada)
  - Testar `build_lap_comparison_chart` retorna um `go.Figure` com 2 traces
  - Testar `generate_dashboard` cria o arquivo no caminho especificado
  - Testar que o HTML gerado contém o nome da sessão e a string "plotly"
  - Usar `tmp_path` fixture do pytest para o arquivo de saída
- **Demo:** executar com dados fake via teste gera um `dashboard.html` abrível no browser com o gráfico visível.

### Task 6: Implementar o entrypoint CLI (`cli.py`) e integrar tudo

- **Objetivo:** conectar todas as camadas em um script executável que aceita argumentos do usuário e produz o dashboard.
- **Implementação:**
  - Usar `argparse`: `--year` (int, obrigatório), `--gp` (str, obrigatório, ex.: "Brazil"), `--session` (str, obrigatório, ex.: "Race"), `--output` (str, opcional, default: `dashboard.html`)
  - Função `main()`:
    1. Parsear argumentos
    2. Instanciar `OpenF1Client()`
    3. Chamar `resolve_session(client, year, gp, session_name)`
    4. Chamar `fetch_drivers`, `fetch_laps`, `fetch_stints`, `fetch_pits`
    5. Chamar `generate_dashboard(..., output_path=output)`
    6. Imprimir: `Dashboard gerado: {output}`
  - Tratar `ValueError` (sessão não encontrada) e `Exception` genérica com mensagem amigável e `sys.exit(1)`
  - Registrar o entrypoint no `pyproject.toml`: `[project.scripts] f1-dashboard = "f1.cli:main"`
- **Testes** (`tests/test_cli.py`):
  - Mockar `resolve_session`, `fetch_*` e `generate_dashboard`
  - Testar que `main()` chama `generate_dashboard` com os parâmetros corretos
  - Testar que `ValueError` resulta em `sys.exit(1)`
- **Demo:** `poetry run f1-dashboard --year 2023 --gp Monaco --session Race --output monaco_race.html` gera o arquivo com comparativo de voltas de todos os pilotos.

### Task 7: Finalizar documentação e validação completa de qualidade

- **Objetivo:** documentar o projeto e garantir que todos os critérios do SKILL.md estão satisfeitos.
- **Implementação:**
  - `docs/index.md` — visão geral: o que é o projeto, descrição do dashboard, link para guia de uso
  - `docs/guia-de-uso.md` — instalação passo a passo, exemplos de uso do CLI com diferentes GPs/anos, como interpretar o dashboard
  - `docs/arquitetura.md` — descrição das 5 camadas com diagrama de fluxo em mermaid
  - `docs/api-reference.md` — endpoints OpenF1 consumidos e mapeamento para os modelos Python
  - Atualizar `mkdocs.yml` com navegação completa entre as 4 páginas
- **Validação final (checklist do SKILL.md):**
  ```bash
  poetry run ruff check src tests
  poetry run ruff format src tests --check
  poetry run pytest
  poetry run mkdocs build --strict
  ```
- **Demo:** todos os 4 comandos acima passam sem erros.

## Definition of Done

Uma tarefa só é considerada finalizada quando todos os itens abaixo forem verdadeiros:

- [ ] Código implementado em `src/f1/`, seguindo a estrutura existente
- [ ] Testes criados/atualizados em `tests/` cobrindo a mudança
- [ ] `poetry run ruff check src tests` sem erros
- [ ] `poetry run ruff format src tests --check` sem pendências
- [ ] `poetry run pytest` passando, com cobertura de `src/f1` ≥ 50%
- [ ] Documentação em `docs/` atualizada, se houve mudança de comportamento/API/configuração
- [ ] `poetry run mkdocs build --strict` concluído sem erros
- [ ] Nenhuma alteração fora do escopo da tarefa solicitada
