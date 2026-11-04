# Losen

En KI-assistent som hjelper deg med datamaskinen ved å bruke det samme grensesnittet som deg selv, slik at alt den gjør kan **sees, forstås og stoppes**. Losen bygger på [Agent S3](https://github.com/simular-ai/Agent-S) fra Simular.

> **Status:** tidlig utvikling (iterasjon 0). Ikke klar for sluttbrukere.
>
> **Advarsel:** `losen-s3` har Losens tilpasninger av S3-prompten, men ikke Losens godkjenning ennå. Den kommer i iterasjon 1. Agenten utfører hvert steg uten å spørre. Bruk bare ufarlige oppgaver, og stopp ved å dra musen helt opp i øvre venstre hjørne eller med Ctrl+C.

- Konseptet: [docs/konsept.md](docs/konsept.md)
- Planen: [docs/plan.md](docs/plan.md)

## Oppsett (macOS, Windows, Linux)

Krav:

- Python **3.11**. S3 støtter i praksis 3.9–3.11.
- git
- Tesseract (OCR), som S3 bruker:
  - macOS: `brew install tesseract`
  - Linux: `sudo apt install tesseract-ocr`
  - Windows: installer Tesseract og legg den i PATH

```bash
git clone https://github.com/rudsto/losen.git
cd losen
python3.11 -m venv .venv          # Windows: py -3.11 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -e .
```

Første installasjon laster ned flere hundre MB, blant annet PaddlePaddle. Versjonene av S3 og Anthropic-SDK-en er låst i `pyproject.toml`.

**Nøkkel:** Sett `ANTHROPIC_API_KEY` i miljøet (se `.env.example`). Bruk en egen nøkkel med kostnadstak. Legg aldri nøkler, logger eller skjermbilder i repoet.

## Kjør (krever et skrivebord)

På macOS må appen du kjører fra (for eksempel Terminal) ha **Tilgjengelighet** og **Skjermopptak** (Systeminnstillinger → Personvern og sikkerhet).

```bash
losen-s3 \
  --provider anthropic --model claude-sonnet-5-5 \
  --ground_provider anthropic --ground_url https://api.anthropic.com \
  --ground_model claude-sonnet-5-5 \
  --grounding_width 1470 --grounding_height 956
```

`--grounding_width/height` må kalibreres per skjerm når Claude er grounding-modell. Verdiene over gjelder utviklerens Mac.

## Tester

| Nivå | Krever | Kommando |
|---|---|---|
| 1 – offline | Python-miljøet | `python tests/run_checks.py` |
| 2 – API | `ANTHROPIC_API_KEY` (små kall, koster litt) | `python tests/run_checks.py --api` |
| 3 – skrivebord | Skjerm og tillatelser | Kjør `losen-s3` med en ufarlig oppgave |
| 4 – eval | Som nivå 3, helst i en VM | Kommer i iterasjon 2 |

**Sky og Linux uten skjerm:** S3 importerer pyautogui, som krever en skjerm. Kjør nivå 1 og 2 med en virtuell skjerm: `xvfb-run python tests/run_checks.py` (ikke testet ennå).

## Struktur

| Sti | Innhold |
|---|---|
| `src/losen/s3_adapt.py` | Losens tilpasninger av S3, lagt inn i minnet ved oppstart. S3-filene endres ikke. |
| `src/losen/run_s3.py` | Kommandoen `losen-s3` |
| `tests/` | Testnivå 1 og 2 |
| `docs/konsept.md` | Konseptet og beslutningene |
| `docs/plan.md` | Iterasjoner, arbeidsform og evaluering |

## Arbeidsform

`main` skal alltid kunne kjøres. Arbeid skjer i grener og kommer inn via pull request, én milepæl per iterasjon. Se [docs/plan.md](docs/plan.md).

## Kreditering

Losen bruker [Agent S](https://github.com/simular-ai/Agent-S) av Simular, lisensiert under Apache-2.0, som avhengighet. `src/losen/s3_adapt.py` inneholder korte utdrag tilpasset fra S3-prompten. Agent S og Simular er varemerker for sine eiere. Losen er ikke tilknyttet Simular.
