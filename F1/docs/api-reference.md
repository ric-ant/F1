# Referência da API OpenF1

Este projeto consome a [API OpenF1](https://openf1.org) — uma API REST open-source com dados de telemetria, timing e sessões da Fórmula 1.



- **Base URL:** `https://api.openf1.org/v1/`
- **Autenticação:** não necessária para dados históricos (a partir de 2023)
- **Rate limit (tier gratuito):** 3 req/s e 30/min
- **Formato:** JSON (padrão)

## Endpoints Utilizados

### `GET /meetings`

Retorna informações sobre fins de semana de corrida (Grande Prêmios).

**Parâmetros usados:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `year` | inteiro | Ano do campeonato |
| `country_name` | string | Nome do país (ex.: `Monaco`, `Brazil`) |

**Modelo Python:** usado internamente para obter o `meeting_key`.

**Exemplo:**
```
GET /meetings?year=2023&country_name=Monaco
```

---

### `GET /sessions`

Retorna informações sobre sessões específicas (treino, qualificação, corrida).

**Parâmetros usados:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `meeting_key` | inteiro | Chave do fim de semana (obtida de `/meetings`) |
| `session_name` | string | Tipo de sessão (`Race`, `Qualifying`, `Sprint`, etc.) |

**Modelo Python:** `Session(session_key, session_name, date_start, country_name)`

**Exemplo:**
```
GET /sessions?meeting_key=1208&session_name=Race
```

---

### `GET /drivers`

Retorna informações dos pilotos participantes de uma sessão.

**Parâmetros usados:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `session_key` | inteiro | Chave da sessão |

**Modelo Python:** `Driver(driver_number, full_name, team_name, name_acronym)`

**Exemplo:**
```
GET /drivers?session_key=9222
```

---

### `GET /laps`

Retorna dados de cada volta percorrida por cada piloto.

**Parâmetros usados:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `session_key` | inteiro | Chave da sessão |

**Modelo Python:** `Lap(driver_number, lap_number, lap_duration, duration_sector_1, duration_sector_2, duration_sector_3)`

> **Nota:** `lap_duration` pode ser `None` em voltas de entrada/saída do pit stop.

**Exemplo:**
```
GET /laps?session_key=9222
```

---

### `GET /stints`

Retorna os stints (períodos com o mesmo conjunto de pneus) de cada piloto.

**Parâmetros usados:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `session_key` | inteiro | Chave da sessão |

**Modelo Python:** `Stint(driver_number, lap_start, lap_end, compound, tyre_age_at_start)`

**Exemplo:**
```
GET /stints?session_key=9222
```

---

### `GET /pit`

Retorna os pit stops realizados durante a sessão.

**Parâmetros usados:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `session_key` | inteiro | Chave da sessão |

**Modelo Python:** `Pit(driver_number, lap_number, pit_duration)`

**Exemplo:**
```
GET /pit?session_key=9222
```

---

## Fluxo de Resolução de Sessão

Para encontrar a `session_key` correta a partir dos parâmetros do usuário:

```
1. GET /meetings?year={year}&country_name={gp}
   → obtém meeting_key

2. GET /sessions?meeting_key={meeting_key}&session_name={session}
   → obtém session_key

3. GET /drivers?session_key={session_key}
   GET /laps?session_key={session_key}
   GET /stints?session_key={session_key}
   GET /pit?session_key={session_key}
```

## Chaves de Referência

- `meeting_key`: identifica o fim de semana de corrida (use `latest` para o atual)
- `session_key`: identifica a sessão específica (use `latest` para a atual)
- `driver_number`: número do piloto na temporada

## Aviso Legal

OpenF1 é um projeto independente, não afiliado oficialmente à Fórmula 1/FIA. Uso destinado a fins educacionais, pessoais e não comerciais.
