# Losen

En KI-assistent som hjelper deg med datamaskinen ved å bruke det samme grensesnittet som deg selv, slik at alt den gjør kan **sees, forstås og stoppes**. Losen bygger på [Agent S3](https://github.com/simular-ai/Agent-S) fra Simular.

> **Status:** tidlig utvikling (v0). Ikke klar for sluttbrukere.
>
> **Advarsel:** `bin/losen-s3` har Losens tilpasninger av S3-prompten, men ikke Losens godkjenning ennå. Agenten utfører hvert steg uten å spørre. Bruk bare ufarlige oppgaver, og stopp ved å dra musen helt opp i øvre venstre hjørne eller med Ctrl+C.

Konseptet er beskrevet i [docs/konsept.md](docs/konsept.md).

## Kom i gang (utvikler, macOS)

Krav:

- Agent S3 (`gui-agents==0.3.2`) i et Python 3.11-miljø i `~/agent-s/.venv`. Stien står i `bin/losen-s3`.
- `ANTHROPIC_API_KEY` satt i miljøet, helst en nøkkel med kostnadstak.
- Terminal med tilgang til Tilgjengelighet og Skjermopptak (Systeminnstillinger → Personvern og sikkerhet).

Kjør S3 med Losens tilpasninger (samme flagg som `agent_s`):

```bash
bin/losen-s3 \
  --provider anthropic --model claude-sonnet-5-5 \
  --ground_provider anthropic --ground_url https://api.anthropic.com \
  --ground_model claude-sonnet-5-5 \
  --grounding_width 1470 --grounding_height 956
```

`--grounding_width/height` må kalibreres for skjermen din når Claude brukes som grounding-modell.

Tester (gjør noen små, betalte kall til Claude):

```bash
sh tests/run_checks.sh
```

## Struktur

| Sti | Innhold |
|---|---|
| `src/losen/s3_adapt.py` | Losens tilpasninger av S3, lagt inn i minnet ved oppstart. S3-filene endres ikke. |
| `src/losen/run_s3.py`, `bin/losen-s3` | Kjører S3 sin kommandolinje med tilpasningene |
| `tests/` | Sjekker av prompten og kall til Claude |
| `docs/konsept.md` | Konseptet |

## Kreditering

Losen bruker [Agent S](https://github.com/simular-ai/Agent-S) av Simular, lisensiert under Apache-2.0, som avhengighet. `src/losen/s3_adapt.py` inneholder korte utdrag tilpasset fra S3-prompten. Agent S og Simular er varemerker for sine eiere. Losen er ikke tilknyttet Simular.
