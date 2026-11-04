# Losen

En KI-assistent som hjelper deg med datamaskinen ved å bruke det samme grensesnittet som deg selv, slik at alt den gjør kan **sees, forstås og stoppes**. Losen bygger på [Agent S3](https://github.com/simular-ai/Agent-S) fra Simular.

> **Status:** del 1, for utvikleren selv, er under arbeid. Ikke klar for andre brukere.
>
> **Bruk `losen`.** Den spør før hver handling (j/n/s). `losen-s3` er S3 sin egen kommandolinje med Losens tilpasninger av prompten, men *uten* godkjenning: agenten utfører hvert steg uten å spørre. Bruk bare ufarlige oppgaver, og stopp ved å dra musen helt opp i et hjørne eller med Ctrl+C.

- Konseptet: [docs/konsept.md](docs/konsept.md)
- Planen: [docs/plan.md](docs/plan.md)
- Erfaringer fra egen bruk: [docs/erfaringer.md](docs/erfaringer.md)

## To deler

| | Del 1 – Losen for meg | Del 2 – Losen for andre |
|---|---|---|
| Hvem | Utvikleren selv | Usikre brukere, først pensjonister |
| Grensesnitt | Terminalen: godkjenn hvert steg (j/n/stopp) | Sluttbrukervindu på enkel norsk |
| Plattform | Mac | macOS og Windows, senere Linux og Android |
| Status | Under arbeid | Starter når del 1 er i daglig bruk |

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
losen "Åpne Kalkulator og regn ut 2+2" --grounding_width 1470 --grounding_height 956
```

For hvert steg viser `losen` refleksjonen, planen (S3 sin *Next Action*, på engelsk), handlingen og koden som skal kjøres. Du svarer:

- **j**: utfør
- **n**: ikke utfør. Du kan skrive hvorfor, og agenten får beskjed og prøver noe annet.
- **s**: stopp. Ctrl+C og musen i et hjørne stopper også.

Venting og notater i agentens tekstbuffer er ikke handlinger på skjermen. De vises, men spørres ikke om. Når agenten sier at den er ferdig, må du sjekke resultatet selv.

Standardmodellen er `claude-sonnet-5-5`, både som generator og grounding-modell. Flaggene er de samme som for `losen-s3` (`--provider`, `--model`, `--ground_provider`, `--ground_url`, `--ground_model`, `--max_trajectory_length`), i tillegg til `--maks_steg` (standard 15), `--logg` (standard `logs`) og `--hurtigtaster` (av som standard). Alle kan settes som miljøvariabler med prefikset `LOSEN_`, for eksempel `LOSEN_GROUNDING_WIDTH=1470`. Flagget vinner over miljøvariabelen. Nøkkelen kan bare settes med `ANTHROPIC_API_KEY`.

`--grounding_width/height` må kalibreres per skjerm når Claude er grounding-modell. Verdiene over gjelder utviklerens Mac.

**Prøv uten skjerm og modell:** `losen --falsk "Prøv sløyfen"` kjører en falsk S3 med faste steg. Ingenting skjer på skjermen, og ingen modell kalles.

**Hendelseslogg:** Hver økt skrives til `logs/losen-<tid>.jsonl`, med én hendelse per linje: tidspunkt, økt, steg, type, plan, handling, kode, valg og tokens. Skjermbilder logges ikke, men planen beskriver skjermen. `logs/` committes aldri.

S3 sin egen kommandolinje, uten godkjenning:

```bash
losen-s3 \
  --provider anthropic --model claude-sonnet-5-5 \
  --ground_provider anthropic --ground_url https://api.anthropic.com \
  --ground_model claude-sonnet-5-5 \
  --grounding_width 1470 --grounding_height 956
```

## Tester

| Nivå | Krever | Kommando |
|---|---|---|
| 1 – offline | Python-miljøet | `python tests/run_checks.py` |
| 2 – API | `ANTHROPIC_API_KEY` (små kall, koster litt) | `python tests/run_checks.py --api` |
| 3 – skrivebord | Skjerm og tillatelser | Kjør `losen` med en ufarlig oppgave |

Nivå 1 dekker S3-tilpasningene, sløyfen med falsk S3, hendelsesloggen, kommandolinjen og koblingen mot ekte AgentS3-objekter. Nivå 2 kjører i tillegg sløyfen mot Claude med et kunstig skjermbilde. Den avviser første forslag og stopper på det andre, så ingenting skjer på skjermen.
| 4 – eval | Som nivå 3, helst i en VM | Kommer i del 2 |

**Sky og Linux uten skjerm:** S3 importerer pyautogui, som krever en skjerm. Kjør nivå 1 og 2 med en virtuell skjerm: `xvfb-run python tests/run_checks.py` (ikke testet ennå).

## Struktur

| Sti | Innhold |
|---|---|
| `src/losen/s3_adapt.py` | Losens tilpasninger av S3, lagt inn i minnet ved oppstart. S3-filene endres ikke. |
| `src/losen/cli.py` | Kommandoen `losen` |
| `src/losen/kjerne.py` | Sløyfen: predict, godkjenning, utføring og hendelser. Kjenner ikke S3. |
| `src/losen/motor.py` | AgentS3 bak kjernens grensesnitt, og beskjeder til agenten ved avvisning |
| `src/losen/terminal.py` | Terminalgrensesnittet: viser hendelser og spør j/n/s |
| `src/losen/hendelser.py` | Hendelsesloggen i JSONL |
| `src/losen/falsk_s3.py` | Falsk S3 for tester og `losen --falsk` |
| `src/losen/run_s3.py` | Kommandoen `losen-s3` |
| `tests/` | Testnivå 1 og 2 |
| `docs/konsept.md` | Konseptet og beslutningene |
| `docs/plan.md` | Iterasjoner, arbeidsform og evaluering |
| `docs/erfaringer.md` | Funn fra egen bruk, som grunnlag for del 2 |

## Arbeidsform

`main` skal alltid kunne kjøres. Arbeid skjer i grener og kommer inn via pull request, én milepæl per iterasjon. Se [docs/plan.md](docs/plan.md).

## Kreditering

Losen bruker [Agent S](https://github.com/simular-ai/Agent-S) av Simular, lisensiert under Apache-2.0, som avhengighet. `src/losen/s3_adapt.py` inneholder korte utdrag tilpasset fra S3-prompten. Agent S og Simular er varemerker for sine eiere. Losen er ikke tilknyttet Simular.
