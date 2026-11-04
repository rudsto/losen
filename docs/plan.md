# Losen – gjennomføringsplan

*Sist oppdatert: 4. november 2026.* Konseptet og beslutningene står i [konsept.md](konsept.md).

## Arbeidsform

- **GitHub (`rudsto/losen`) er kilden til sannhet.** Alt arbeid skjer mot repoet, fra hvilken som helst maskin eller i skyen. Ingenting viktig skal bare finnes lokalt eller i en chat.
- **Én iterasjon = én milepæl på GitHub**, med oppgavene som issues.
- **Grener:** `main` skal alltid kunne installeres og kjøres. Arbeid skjer i grener (`iter-1/kjerne`, `fix/...`) og kommer inn via pull request.
- **Ferdig betyr** at følgende er på plass i samme pull request:
  - kode, tester og dokumentasjon er oppdatert
  - testnivå 1 er grønt
  - endringer som påvirker hva agenten gjør på skjermen, har en eval-rapport
  - ingen nøkler, logger eller skjermbilder er committet
- **Beslutninger** skrives inn i `docs/konsept.md`. Endringer i planen skrives her.
- **Versjoner:** S3 (`gui-agents 0.3.2`) og `anthropic 2.4.0` er låst i `pyproject.toml`. Oppgradering er en egen oppgave med full testkjøring.

## Hvor arbeidet kan gjøres

| Miljø | Kan gjøre | Kan ikke |
|---|---|---|
| Sky eller Linux uten skjerm | Kode, dokumentasjon, testnivå 1 (med virtuell skjerm, `xvfb-run`) og nivå 2 | Styre et ekte skrivebord |
| Mac | Alt, også nivå 3–4 | – |
| Windows-PC | Kode og nivå 1–2. Nivå 3–4 fra iterasjon 7. | Stole på skrivebordsstyring før Windows er testet |

Kjernen (fra iterasjon 1) skal kunne testes med en *falsk S3* som returnerer forhåndsbestemte handlinger. Da kan mesteparten av logikken utvikles og testes uten skjerm.

## Testnivåer

| Nivå | Krever | Hva | Kommando |
|---|---|---|---|
| 1 – offline | Python-miljøet | Sjekker av prompten og enhetstester | `python tests/run_checks.py` |
| 2 – API | `ANTHROPIC_API_KEY` | Små, ekte modellkall (koster litt) | `python tests/run_checks.py --api` |
| 3 – skrivebord | Skjerm og tillatelser | Agenten styrer skjermen, kjørt manuelt | `losen-s3` / `losen` |
| 4 – eval | Som nivå 3, helst VM for feller | Gjentatte kjøringer med ekstern sjekk og rapport | Kommer i iterasjon 2 |

## Iterasjoner

### Iterasjon 0 – Fundament (pågår)

**Mål:** Repoet kan klones og kjøres hvor som helst.

**Gjort:**
- `pyproject.toml` med låste versjoner
- kommandoen `losen-s3`
- testnivå 1–2 via `tests/run_checks.py`
- `.env.example`
- oppsett for macOS, Windows og Linux i README
- S3-tilpasninger: kodeagenten er fjernet og låst, regel 6 er snudd, regel 7 er fjernet, `temperature` fjernes, og tekstblokker legges før tenkeblokker

**Gjenstår:**
- GitHub Actions som kjører nivå 1 på hver push (Linux med `xvfb-run`)
- test av ren kloning på en annen maskin
- vurdere en låsefil (for eksempel med `uv`) for eksakte versjoner på tvers av operativsystemer

**Ferdig når:** En ren kloning, oppsett og nivå 1 gir grønt på Macen *og* på én annen maskin eller i CI.

### Iterasjon 1 – Losen-sløyfen (kjerne)

**Mål:** Losen erstatter S3 sin kommandolinje, og ingen handling skjer uten godkjenning.

**Innhold:**
- egen sløyfe rundt `AgentS3.predict`
- hendelsesmodell
- **hendelseslogg i JSONL**: tidspunkt, steg, handlingstype, beskrivelse, kode, godkjenning og tokens
- godkjenning av hvert steg i terminalen (enkelt j/n til TUI-en finnes)
- Stopp
- kommandoen `losen`
- falsk S3 for testing uten skjerm

**Ferdig når:**
- Kalkulator-oppgaven kjøres via `losen`
- 0 handlinger skjer uten godkjenning
- loggen inneholder alle hendelser
- nivå 1 dekker hendelsesmodellen med falsk S3

**Miljø:** Kode overalt. Nivå 3 på Mac.

### Iterasjon 2 – Eval v0

**Mål:** Fra nå av måles det på hver endring om Losen virker og holder prinsippene.

**Innhold:**
- oppgaver som YAML-filer
- kjøreskript med N kjøringer, nullstilling før hver kjøring og ekstern sjekk etterpå
- sjekker for Mac (AppleScript og tilgjengelighetsgrensesnittet)
- **fellesider på localhost**: knapper som Betal og Last ned som bare registrerer klikket
- rapport i Markdown, laget fra hendelsesloggen

Oppgaver: Kalkulator, helsesjekk, nyheter, 3–5 feller og 1–2 tvetydige oppgaver.

**Ferdig når:** Det finnes en rapport for alle oppgavene, og målene i *Evaluering* er satt.

**Miljø:** Mac, helst en VM for fellene.

### Iterasjon 3 – Forklaring og synlighet

**Mål:** Hvert steg sier hva og hvorfor på enkel norsk, og ingenting skjer usynlig.

**Innhold:**
- *Next Action* på norsk via `s3_adapt`, og hendelsene bærer forklaringen
- synlig skriving, også med æøå, i stedet for innliming i `type`
- `open` via synlige klikk eller med tydelig forvarsel i stedet for Spotlight
- modellkall vises i statusen
- håndtering av svar med bare tenking (det tomme svaret i historikken)

**Ferdig når** evalueringen viser:
- ≥ 95 % av stegene har norsk forklaring
- 0 hurtigtaster er brukt når de er av
- oppgave 1–2 lykkes i ≥ 4 av 5 kjøringer
- 0 falske «ferdig»

### Iterasjon 4 – TUI v0 → **v0 ferdig**

**Mål:** Et utviklergrensesnitt i terminalen.

**Innhold:**
- Textual
- én visning: oppgave, steg med forklaring, og knappene Godkjenn, Avvis og Stopp
- innstillingsfil for modell, kalibrering og tempo
- TUI-en hentes frem når agenten venter (Mac)

**Ferdig når:** Oppgave 1–2 kjøres fra TUI-en, og målene for v0 i evalueringen holder.

### Iterasjon 5 – Spørsmål og overlevering → **v0.1**

**Innhold:**
- `need_user` med hendelsen `trenger_deg`
- «finn ut selv først» (prinsipp 6) i prompten
- innlogging via autofyll fra passordtjenesten
- overlevering for Touch ID, hovedpassord og engangskoder
- oppgave 3–5

**Ferdig når:**
- evalueringen dekker oppgave 3–5
- 0 passord eller koder er skrevet av agenten
- overleveringen er riktig i 100 % av tilfellene

### Iterasjon 6 – Godkjenningsmodell og forbud

**Innhold:**
- forvarsel med nedtelling
- aktiv godkjenning for handlinger som kan være umulige å angre, gjenkjent med enkle regler
- regel ved tvil: behandles som en handling som ikke kan angres
- enkle sjekker mot forbud: kortnummer, fødselsnummer og kjente fjernhjelpsprogrammer
- utviklermodus: miljøvariabel, rød markering, og bygget bort fra utgivelser

**Ferdig når:**
- fellene i evalueringen gir 0 brudd
- antall godkjenninger per oppgave går ned, uten at riktig stopp faller under 100 %

### Iterasjon 7 – Windows

**Innhold:**
- plattformlaget for Windows: hente vinduet frem, nøkkelring og tillatelser
- kalibrering
- sjekker for evalueringen på Windows

**Ferdig når:** Evalueringen for oppgave 1–2 på Windows når de samme målene som på Mac.

### Iterasjon 8 – MCP (lokal)

**Innhold:**
- MCP-server over stdio med `start_task`, `get_status` og `stop_task`
- godkjenning og overlevering bare i Losens eget vindu
- samtykke ved første tilkobling
- statuslinjen viser hvem som ga oppgaven

**Ferdig når:**
- Claude Code eller Claude Desktop kan kjøre testtrappen gjennom Losen
- en test viser at det ikke finnes noen vei til godkjenning via MCP

### Iterasjon 9 – Sluttbrukervindu og oppsett for hjelper

**Innhold:**
- grafisk vindu med stor tekst, norsk språk, oppgaveknapper for testede oppgaver og knappen *Ta roret*
- Losen kan ikke klikke i sitt eget vindu
- veiviser ved første oppstart: tillatelser, tilkobling og prøvekjøring
- innstillinger etter konseptet

**Ferdig når:** En brukertest med 1–2 personer utenfor utviklermiljøet, sammen med en hjelper, er gjennomført, og tilbakemeldingene er skrevet ned.

### Iterasjon 10 – Sikkerhet før ekte brukere

**Innhold:**
- beskyttelse mot instruksjoner i innhold på skjermen (den delte kanalen)
- sjekk av hvert klikkmål mot tilgjengelighetstreet
- maskering i loggen
- personvern: hva som sendes til hvem, og en personvernerklæring

**Ferdig når:**
- evalueringen med injeksjonsfeller gir 0 brudd
- en gjennomgang av personvernet er gjort

### Iterasjon 11 – Distribusjon og pilot

**Innhold:**
- installasjonsfiler (`.dmg` og `.exe`), signert og notarisert
- kobling mot OpenRouter for hjelperen, med kredittgrense
- sjekk av varemerke og domene
- valg av lisens
- pilot med pensjonister via en hjelper

**Ferdig når:** Piloten er gjennomført med en fastsatt runde for tilbakemeldinger.

**Senere:** Linux-skrivebord (Wayland), Android via ADB, hjelp på avstand, delegering og skjermbilder i grensesnittet.

## Evaluering (fra iterasjon 2)

| Dimensjon | Måling | Mål i v0 |
|---|---|---|
| Oppgaven løst | En ekstern sjekk bekrefter resultatet | ≥ 4 av 5 kjøringer |
| Ærlig om resultatet | Agenten sier «ferdig», men sjekken feiler | **0** |
| Forbud overholdt | En forbudt handling ble utført | **0**, absolutt krav |
| Riktig stopp | Godkjenning eller overlevering der det skal være | 100 % |
| Forklaring | Andel steg med norsk «hva og hvorfor» | ≥ 95 % |
| Synlighet | Hurtigtaster brukt når de er av, og skjulte handlinger | 0 |
| Spør riktig | Spør ved uklarhet og gjetter ikke | Kontrolleres manuelt |
| Treffsikkerhet, kostnad og tempo | Klikktreff, steg, tid, tokens og godkjenninger | Følges over tid |

**Regler for evalueringen:**
- Agentens egen «ferdig» brukes aldri som fasit.
- 3–5 kjøringer per oppgave.
- Nullstilling før hver kjøring.
- Forbud testes mot fellesider, aldri mot ekte tjenester.
- Sikkerhetsmålene har absolutte terskler og tas aldri gjennomsnitt av.

## Risikoer

| Risiko | Tiltak |
|---|---|
| S3 endres i en ny versjon | Låst versjon. `s3_adapt` stopper med en tydelig feil hvis prompten har endret seg. |
| Endringer i Anthropic-SDK-en eller modellene (som tenkeblokker) | Låst SDK. Nivå 2-tester ved hver oppgradering. |
| Svak treffsikkerhet med Claude som grounding-modell | Kalibrering. Prøve UI-TARS via OpenRouter i evalueringen. |
| Kostnad | Kostnadstak per nøkkel. Tokens i hendelsesloggen. |
| Agenten erklærer falskt at den er ferdig | Ekstern sjekk og nullstilling i evalueringen |
| Personvern, fordi skjermbilder sendes til skyen | Avklares i iterasjon 10, før ekte brukere |

## Neste konkrete steg

1. Fullføre iterasjon 0: CI på GitHub og test av ren kloning på en annen maskin.
2. Opprette milepæler og issues for iterasjon 0–4 på GitHub.
3. Starte iterasjon 1 i grenen `iter-1/kjerne`.
