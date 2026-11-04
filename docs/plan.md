# Losen – gjennomføringsplan

*Sist oppdatert: 4. november 2026.*

- Konseptet og beslutningene: [konsept.md](konsept.md)
- Erfaringer fra egen bruk: [erfaringer.md](erfaringer.md)

## To deler

| | Del 1 – Losen for meg | Del 2 – Losen for andre |
|---|---|---|
| Hvem | Utvikleren selv | Usikre brukere, først pensjonister, med en hjelper som setter opp |
| Mål | Et verktøy der agenten gjør oppgaver på Macen mens jeg ser på og godkjenner hvert steg | En trygg og forståelig assistent som andre kan stole på |
| Grensesnitt | Terminalen (j/n/stopp) | Sluttbrukervindu på enkel norsk |
| Plattform | Mac | macOS og Windows, senere Linux og Android |
| Start | Nå | Når del 1 er i daglig bruk |

**To ting fra konseptet gjelder også i del 1:** godkjenning før hver handling, og at kjernen sender hendelser som logges. Det koster lite nå, og det gjør at del 2 bygger videre på del 1 i stedet for å starte på nytt.

## Arbeidsform

- **GitHub (`rudsto/losen`) er kilden til sannhet.** Alt arbeid skjer mot repoet, fra hvilken som helst maskin eller i skyen. Ingenting viktig skal bare finnes lokalt eller i en chat.
- **Én iterasjon = én milepæl på GitHub**, med oppgavene som issues.
- **Grener:** `main` skal alltid kunne installeres og kjøres. Arbeid skjer i grener (`iter-1.1/sloyfe`, `fix/...`, `docs/...`) og kommer inn via pull request.
- **Ferdig betyr** at følgende er på plass i samme pull request:
  - kode, tester og dokumentasjon er oppdatert
  - testnivå 1 er grønt
  - ingen nøkler, logger eller skjermbilder er committet
  - i del 2 også: endringer som påvirker hva agenten gjør på skjermen, har en eval-rapport
- **Beslutninger** skrives inn i `docs/konsept.md`, endringer i planen her, og funn fra bruk i `docs/erfaringer.md`.
- **Versjoner:** S3 (`gui-agents 0.3.2`) og `anthropic 2.4.0` er låst i `pyproject.toml`. Oppgradering er en egen oppgave med full testkjøring.

## Hvor arbeidet kan gjøres

| Miljø | Kan gjøre | Kan ikke |
|---|---|---|
| Sky eller Linux uten skjerm | Kode, dokumentasjon, testnivå 1 (med `xvfb-run`) og nivå 2 | Styre et ekte skrivebord |
| Mac | Alt, også nivå 3–4 | – |
| Windows-PC | Kode og nivå 1–2. Nivå 3–4 når Windows er testet (del 2). | – |

Kjernen skal kunne testes med en *falsk S3* som returnerer forhåndsbestemte handlinger. Da kan mesteparten av logikken utvikles og testes uten skjerm.

## Testnivåer

| Nivå | Krever | Hva | Kommando |
|---|---|---|---|
| 1 – offline | Python-miljøet | Sjekker av prompten og enhetstester | `python tests/run_checks.py` |
| 2 – API | `ANTHROPIC_API_KEY` | Små, ekte modellkall (koster litt) | `python tests/run_checks.py --api` |
| 3 – skrivebord | Skjerm og tillatelser | Agenten styrer skjermen, kjørt manuelt | `losen` / `losen-s3` |
| 4 – eval | Som nivå 3, helst VM for feller | Gjentatte kjøringer med ekstern sjekk og rapport | Del 2, iterasjon 2.1 |

---

## Del 1 – Losen for meg

### Iterasjon 1.0 – Fundament (pågår)

**Mål:** Repoet kan klones og kjøres hvor som helst.

**Gjort:**
- `pyproject.toml` med låste versjoner
- kommandoen `losen-s3`
- testnivå 1–2 via `tests/run_checks.py`
- `.env.example`
- oppsett for macOS, Windows og Linux i README
- S3-tilpasninger: kodeagenten er fjernet og låst, regel 6 er snudd, regel 7 er fjernet, `temperature` fjernes, og tekstblokker legges før tenkeblokker
- ren kloning på Windows-PC-en (4. november 2026): Python 3.11.9, Tesseract 5.4, `pip install -e .`, og nivå 1 og 2 er grønne
- GitHub Actions (`.github/workflows/niva1.yml`) som kjører nivå 1 på hver push og pull request, på Linux med `xvfb-run` og på Windows
- `CLAUDE.md` med reglene for Claude Code i repoet

**Gjenstår:**
- se at arbeidsflyten blir grønn på GitHub etter første push

**Ferdig når:** En ren kloning, oppsett og nivå 1 gir grønt på Macen *og* på én annen maskin eller i CI.

### Iterasjon 1.1 – Sløyfen (kode ferdig, prøve på Mac gjenstår)

**Mål:** `losen` erstatter S3 sin kommandolinje, og ingen handling skjer uten godkjenning.

**Gjort (4. november 2026, grenen `iter-1.1/sloyfe`):**
- `kjerne.py`: sløyfen. `utfør()` kalles bare etter **j**. Venting og notater vises og logges, men kjøres ikke som kode.
- `motor.py`: AgentS3 bak kjernens grensesnitt. Ved **n** eller feil i utføringen legges en beskjed foran neste melding til generatoren og refleksjonen.
- `terminal.py` og `cli.py`: kommandoen `losen`, og `losen --falsk` for å prøve uten skjerm og modell
- `hendelser.py`: JSONL i `logs/`. Tokens kommer fra hvert Anthropic-kall via `s3_adapt`.
- nivå 1: `check_kjerne.py` (falsk S3) og `check_motor.py` (ekte AgentS3-objekter, uten kall). Nivå 2: `check_sloyfe_api.py` (Claude og kunstig skjermbilde, n og s). Alle er grønne på Windows.

**Gjenstår:** Kalkulator-oppgaven og helsesjekken med `losen` på Macen (nivå 3).

**Innhold:**
- egen sløyfe rundt `AgentS3.predict`
- for hvert steg vises planen (S3 sin *Next Action*, på engelsk) og handlingen som skal kjøres
- valg per steg: **j** = utfør, **n** = ikke utfør (agenten får beskjed og prøver noe annet), **s** = stopp
- hendelser i JSONL: tidspunkt, steg, plan, handling, kode, valg og tokens
- kommandoen `losen "oppgave"`, med samme modellvalg som `losen-s3` (flagg og miljøvariabler)
- falsk S3 for testing uten skjerm

**Ferdig når:**
- Kalkulator-oppgaven og helsesjekken kjøres via `losen`
- 0 handlinger skjer uten godkjenning
- loggen inneholder alle hendelser
- nivå 1 dekker sløyfen med falsk S3

### Iterasjon 1.2 – I bruk

**Mål:** Losen brukes til egne oppgaver, og erfaringene skrives ned.

**Innhold:**
- kalibrering av klikk for egen skjerm
- justeringer etter bruk
- funn føres i `docs/erfaringer.md`
- *Valgfritt:* MCP over stdio, så Claude Code kan gi Losen oppgaver. Godkjenningen skjer fortsatt i terminalen.
- *Valgfritt:* en enkel TUI, hvis terminalen blir for knapp

**Ferdig når:** Losen er brukt på egne oppgaver over et par uker, og `erfaringer.md` har funn som kan brukes i del 2.

---

## Del 2 – Losen for andre

Del 2 starter når del 1 er i daglig bruk. Rekkefølgen kan justeres etter erfaringene fra del 1.

### 2.1 – Evaluering

**Innhold:**
- oppgaver som YAML-filer
- kjøreskript med N kjøringer, nullstilling og ekstern sjekk
- sjekker for Mac
- fellesider på localhost
- rapport laget fra hendelsesloggen

**Ferdig når:** Det finnes en rapport for oppgave 1–2, feller og tvetydige oppgaver, og målene i *Evaluering* er satt.

### 2.2 – Forklaring og synlighet

**Innhold:**
- *Next Action* på enkel norsk
- synlig skriving, også med æøå
- `open` uten Spotlight, eller med tydelig forvarsel
- modellkall vises i statusen
- håndtering av svar med bare tenking

**Ferdig når:** ≥ 95 % av stegene har norsk forklaring, 0 hurtigtaster er brukt når de er av, og det er 0 falske «ferdig».

### 2.3 – Spørsmål og overlevering

**Innhold:**
- `need_user` med hendelsen `trenger_deg`
- «finn ut selv først» (prinsipp 6)
- autofyll fra passordtjenesten
- overlevering for Touch ID, hovedpassord og engangskoder
- oppgave 3–5

**Ferdig når:** 0 passord eller koder er skrevet av agenten, og overleveringen er riktig i 100 % av tilfellene.

### 2.4 – Godkjenningsmodell og forbud

**Innhold:**
- forvarsel med nedtelling
- aktiv godkjenning for handlinger som kan være umulige å angre
- regel ved tvil: behandles som en handling som ikke kan angres
- forbudsliste med enkle sjekker
- utviklermodus, bygget bort fra utgivelser
- cookiebannere: «bare nødvendige»

**Ferdig når:** Fellene gir 0 brudd, og det trengs færre godkjenninger uten at riktig stopp faller under 100 %.

### 2.5 – Sluttbrukervindu og oppsett for hjelper

**Innhold:**
- vindu med stor tekst, oppgaveknapper og *Ta roret*
- Losen kan ikke klikke i sitt eget vindu
- veiviser ved første oppstart
- innstillinger etter konseptet

**Ferdig når:** En brukertest med 1–2 personer, sammen med en hjelper, er gjennomført, og tilbakemeldingene er skrevet ned.

### 2.6 – Windows

**Innhold:** plattformlaget for Windows, kalibrering og sjekker for evalueringen.

**Ferdig når:** Evalueringen for oppgave 1–2 når de samme målene som på Mac.

### 2.7 – MCP for andre

**Innhold:**
- samtykke ved første tilkobling
- godkjenning og overlevering bare i Losens eget vindu
- statuslinjen viser hvem som ga oppgaven

**Ferdig når:** En test viser at det ikke finnes noen vei til godkjenning via MCP.

### 2.8 – Sikkerhet før ekte brukere

**Innhold:**
- beskyttelse mot instruksjoner i innhold på skjermen
- sjekk av hvert klikkmål mot tilgjengelighetstreet
- maskering i loggen
- personvern og personvernerklæring

**Ferdig når:** Injeksjonsfellene gir 0 brudd, og en gjennomgang av personvernet er gjort.

### 2.9 – Distribusjon og pilot

**Innhold:**
- installasjonsfiler, signert og notarisert
- kobling mot OpenRouter for hjelperen
- sjekk av varemerke og domene
- valg av lisens
- pilot med pensjonister

**Ferdig når:** Piloten er gjennomført med en fastsatt runde for tilbakemeldinger.

**Senere:** Linux-skrivebord (Wayland), Android via ADB, hjelp på avstand, delegering og skjermbilder i grensesnittet.

---

## Evaluering

**Del 1:**
- testnivå 1–2 og manuelle prøver
- agentens egen «ferdig» brukes aldri som fasit; sjekk resultatet selv
- nullstill før hver prøve

**Del 2:**

| Dimensjon | Måling | Mål |
|---|---|---|
| Oppgaven løst | En ekstern sjekk bekrefter resultatet | ≥ 4 av 5 kjøringer |
| Ærlig om resultatet | Agenten sier «ferdig», men sjekken feiler | **0** |
| Forbud overholdt | En forbudt handling ble utført | **0**, absolutt krav |
| Riktig stopp | Godkjenning eller overlevering der det skal være | 100 % |
| Forklaring | Andel steg med norsk «hva og hvorfor» | ≥ 95 % |
| Synlighet | Hurtigtaster brukt når de er av, og skjulte handlinger | 0 |
| Spør riktig | Spør ved uklarhet og gjetter ikke | Kontrolleres manuelt |
| Treffsikkerhet, kostnad og tempo | Klikktreff, steg, tid, tokens og godkjenninger | Følges over tid |

**Regler:**
- Ekstern sjekk, aldri agentens egen «ferdig».
- 3–5 kjøringer per oppgave.
- Nullstilling før hver kjøring.
- Forbud testes mot fellesider, aldri mot ekte tjenester.
- Sikkerhetsmålene har absolutte terskler og tas aldri gjennomsnitt av.

## Risikoer

| Risiko | Tiltak |
|---|---|
| S3 endres i en ny versjon | Låst versjon. `s3_adapt` stopper med en tydelig feil hvis prompten har endret seg. |
| Endringer i Anthropic-SDK-en eller modellene (som tenkeblokker) | Låst SDK. Nivå 2-tester ved hver oppgradering. |
| Svak treffsikkerhet med Claude som grounding-modell | Kalibrering. Prøve UI-TARS via OpenRouter. |
| Kostnad | Kostnadstak per nøkkel. Tokens i hendelsesloggen. |
| Agenten erklærer falskt at den er ferdig | Sjekk selv i del 1. Ekstern sjekk og nullstilling i del 2. |
| Del 1-valg gjør del 2 vanskelig | Skillet mellom kjerne og grensesnitt og loggen av hendelser holdes fra start |
| Personvern, fordi skjermbilder sendes til skyen | Avklares i 2.8, før ekte brukere |

## Neste konkrete steg

1. Fullføre 1.0: se at CI er grønn på GitHub.
2. Prøve `losen` på Macen med Kalkulator-oppgaven og helsesjekken, og så slå sammen `iter-1.1/sloyfe`.
3. Starte 1.2: kalibrering og egen bruk.
