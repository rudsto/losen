# Losen – konsept

*Sist oppdatert: 4. november 2026. Status: v0 under arbeid.*

Navnet: En los går om bord og fører skipet trygt i havn, mens kapteinen hele tiden har kommandoen. Brukeren er kapteinen.

## Formål

En KI-assistent som hjelper en person med oppgaver på datamaskinen ved å bruke det samme grensesnittet personen selv bruker, slik at alt den gjør kan **sees, forstås og stoppes**. Målet er riktig kalibrert tillit: personen skal kunne se hva assistenten mestrer, og hvor den ikke gjør det.

Bakgrunn: Når en KI-assistent jobber i bakgrunnen eller via terminalen, vet ikke brukeren hva som er gjort, eller om noe har gått galt. Når assistenten bruker de samme kanalene som brukeren, kan brukeren følge med, særlig i starten, og bli trygg på at arbeidet er godt nok.

## Målgruppe

- Unge og eldre som er usikre på digitale verktøy. De første brukerne er trolig pensjonister.
- Skal være god nok til at en utvikler kan bruke den. Første testbruker er utvikleren selv.

## Prinsipper

1. **Synlighet går foran effektivitet.** Synlige klikk og menyer foretrekkes. Hurtigtaster må slås på aktivt.
2. **Hva og hvorfor før hver handling**, kort og meningsfullt, på enkel norsk.
3. **Ingenting skjer skjult.** Hvert steg vises i statuslinjen, også det som ikke skjer på skjermen, som modellkall.
4. **Tillit opparbeides per oppgave og kan mistes.** Assistenten viser tydelig når den er usikker eller feiler.
5. **Tempoet tilpasses brukeren.** Ventetiden før hver handling kan justeres.
6. **Finn ut selv først, spør når noe mangler.** Rekkefølgen er: det brukeren har sagt, det som vises på skjermen, noen få synlige og ufarlige steg, og til slutt et spørsmål. Assistenten graver ikke i private ting den ikke trenger, leter ikke i det uendelige og gjetter aldri der en feil ikke kan angres.

## Arkitektur

| Lag | Innhold |
|---|---|
| Motor | Agent S3 (gui-agents 0.3.2): generator, refleksjon, grounding, tekstspenn. Brukes som avhengighet og redigeres ikke. |
| Kjerne | Losens egen sløyfe: `predict`, vurdering, eventuell godkjenning, `exec` og logg. Håndhever grensene og sender ut hendelser. |
| Grensesnitt | Viser hendelsene og tar imot valg: TUI i v0, sluttbrukervindu senere, MCP for eksterne KI-tjenester. |
| Plattformlag | macOS, Windows og Linux. Android senere via ADB. Her ligger det som er spesifikt for hvert operativsystem: å hente vinduet frem, tillatelser og nøkkellagring. |

**Egen handling i harnessen:** `need_user(beskjed, alternativer)` gir hendelsen `trenger_deg`. Den dekker både spørsmål (manglende informasjon) og overlevering (ting brukeren må gjøre selv: Touch ID, hovedpassord, engangskoder).

**Hendelsesflyt:** `økt_startet` → `vurderer` → `forslag` («Losen foreslår: Klikker på *Fil* fordi …») → `venter_på_godkjenning` → `utført` / `avvist` → `modellkall` → `trenger_deg` → `feil` / `usikker` → `ferdig`.

Grensesnittet kjenner bare hendelsene og vet ingenting om S3.

## De første oppgavene (testtrappen)

| # | Oppgave | Slik gjør Losen det |
|---|---|---|
| 1 | Helsesjekk | Åpner Innstillinger og viser hvor internett og lagringsplass står. Svarer på enkel norsk. |
| 2 | Nyheter | Brukeren sier for eksempel «NRK». Losen åpner nettleseren og går dit. Ingenting lagres. |
| 3 | E-post: innlogging og status | Ser først etter selv (Mail-appen, bokmerker, åpne faner), spør bare hvis det er uklart, og logger inn via passordtjenesten. «Status» betyr antall uleste; ingen e-poster åpnes. |
| 4 | Send e-post til seg selv | Første handling som ikke kan angres, med en ufarlig mottaker. |
| 5 | Innlogging med totrinnsbekreftelse | Overlevering: brukeren skriver eller godkjenner koden selv. |

**Regel for innlogging:** Passordtjenesten fyller inn via autofyll. Losen åpner aldri selve passordtjenesten og blar ikke i den, og passord går aldri gjennom modellen.

**Cookiebannere:** «Bare nødvendige». Finnes ikke den knappen, åpner Losen valgene og slår av alt som er frivillig. Krever siden samtykke eller betaling for å komme inn, spør Losen brukeren.

## Godkjenning

| Lag | Gjelder | Hva brukeren gjør |
|---|---|---|
| Forvarsel med nedtelling | Alle handlinger | Ingenting. Handlingen skjer etter noen sekunder med mindre brukeren stopper den. |
| Aktiv godkjenning | Handlinger som *kan* være umulige å angre, kjent igjen på handlingstype og ord som Send, Slett, Kjøp, Bekreft og Publiser | Må trykke Godkjenn |
| Regel ved tvil | Når harnessen er usikker | Handlingen behandles som en som ikke kan angres |

- «Godkjenn hvert steg» er et strengere valg, og standard i v0.
- **Innstillinger kan bare gjøre ting strengere, aldri løsere.**
- Spørsmål og overlevering stopper uansett.

## Forbudte handlinger

**Aldri automatisk.** Losen nekter, forklarer hvorfor og ber brukeren gjøre det selv.

- Penger: betaling, kjøp, overføringer, nettbank, kryptovaluta.
- Hemmeligheter: skrive inn passord, PIN, BankID- og engangskoder, kortnummer og fødselsnummer. Overlevering brukes i stedet.
- Passordtjenesten: åpne den eller bla i den. Bare autofyll er lov.
- Sikkerhet: endre passord, totrinnsbekreftelse, brannmur, antivirus, systemtillatelser og brukerkontoer. Losen kan heller ikke gi seg selv tillatelser.
- Fjernhjelp: installere eller gi tilgang til fjernstyringsprogrammer (TeamViewer, AnyDesk). Dette er en vanlig svindelmetode mot eldre.
- Programvare: installere og avinstallere programmer, eller åpne nedlastede filer.
- Sletting: tømme papirkurven og slette permanent.
- Avtaler: godta vilkår på brukerens vegne. Unntaket er «bare nødvendige» for cookies.
- System: terminal, administratorpassord og `sudo`.

**Lov, men krever aktiv godkjenning:** sende e-post og meldinger, publisere, sende inn skjemaer, slette til papirkurven, flytte filer, klikke lenker i e-poster og meldinger, og endre innstillinger i apper.

**Håndheving i v0:** gjennom prompten, ved at handlinger er fjernet, og med enkle sjekker. Det er et godt gjerde, ikke en mur. Garantien kommer med sjekken mot tilgjengelighetstreet.

### Utviklermodus

- Slås på med en miljøvariabel eller en egen fil, aldri i grensesnittet.
- Forbudte handlinger krever da aktiv godkjenning i stedet for å være blokkert.
- Rød ramme og statuslinjen «UTVIKLERMODUS: forbudslisten er av» vises hele tiden.
- Varer bare til appen lukkes. Alt logges.
- Bygges bort fra installasjonsfilene sluttbrukere får.

## Grensesnitt

**v0 – TUI for utvikleren (forenklet):** én visning, økt. Den har oppgavefelt, steg med norsk forklaring og knappene Godkjenn, Avvis og Stopp. Resten ligger i en innstillingsfil. TUI-en hentes frem når agenten venter.

**Senere – sluttbrukervindu:**

```
┌───────────────────────────────────────────────┐
│  Hva vil du ha hjelp til?                     │
│  [ Sjekk datamaskinen ]  [ Les nyhetene ]     │
│  [ Sjekk e-posten ]      [ Skriv selv … ]     │
│  ─────────────────────────────────────────    │
│  Losen: Jeg åpner Innstillinger for å se hvor │
│         mye lagringsplass du har.             │
│               [  TA RORET  ]                  │
│ ⚙ Innstillinger                               │
└───────────────────────────────────────────────┘
```

- Oppgaveknapper vises bare for testede oppgaver. Fritekst finnes som et valg.
- Losen kan ikke klikke i sitt eget vindu.
- Språket bruker metaforen: «Losen foreslår …», «Nå har du roret …», «Ta roret» (stopp).

## Innstillinger

- Ingen profil, ingen innlogging og ingen synlighetsnivåer.
- Få innstillinger med trygge standardverdier: tilkobling, tempo, tekststørrelse og språk.
- Sikkerhet ligger i koden og kan ikke slås av.
- Bekreftelse kreves før endringer som kan få appen til å slutte å virke.
- Lagres på standardplassen for hvert operativsystem, i en lesbar fil med versjonsnummer. Nøklene ligger bare i operativsystemets nøkkelring.

## Oppsett, nøkler og kostnad

| | Nå (v0) | Senere |
|---|---|---|
| Installasjon | Python-miljø på utviklerens Mac | Vanlige installasjonsfiler (`.exe`, `.dmg`), signert og notarisert |
| Første oppstart | – | Veiviser for hjelperen: tillatelser, tilkobling, prøvekjøring av helsesjekken |
| Nøkler | Miljøvariabel og nøkkelring | Hjelperen kobler til OpenRouter på stedet (innlogging via OpenRouter), med kredittgrense |
| Betaling | Ingen. Utvikleren betaler leverandøren direkte. | Ingen betaling i appen |

- Kjernen henter nøkler fra en *nøkkelkilde*, slik at nye kilder kan legges til uten endringer andre steder.
- Kostnadstak på hver nøkkel: eget arbeidsområde med grense hos Anthropic, kredittgrense hos OpenRouter.

## MCP – tilkobling fra eksterne KI-tjenester

- **Oppgavenivå:** Den eksterne KI-en gir Losen en oppgave. Losen planlegger, viser, ber om godkjenning og utfører selv.
- Verktøy: `start_task(beskrivelse)`, `get_status(task_id)`, `stop_task(task_id)`.
- Godkjenning, overlevering og spørsmål skjer **bare i Losens eget vindu**, aldri via MCP.
- Bare lokalt (stdio) i starten. Personen ved maskinen må godta tilkoblingen første gang.
- Statuslinjen viser hvem som ga oppgaven. Samme grenser og samme kostnadstak gjelder.
- Kommer etter v0 og før sluttbrukervinduet.

## Tilpasninger av S3 (`src/losen/s3_adapt.py`)

**Gjort og verifisert:**

- Kodeagenten er fjernet fra prompten og låst.
- Regel 7, med OSWorld-passordet og sudo, er fjernet.
- Regel 6 er snudd til synlige klikk. Hurtigtaster er av og låst, og kan slås på med `allow_hotkeys=True`.
- Anthropic-SDK 2.x: `temperature` fjernes, og tekstblokker legges før tenkeblokker i svaret.

**Kjent, ikke løst:**

- `type` limer inn med ⌘V, og `open` bruker Spotlight. Begge er hurtigtaster internt.
- Svarer modellen bare med tenking, legges et tomt svar i historikken, og neste kall feiler.
- Handlingene er kjørbar kode (`exec`). Én skjerm forutsettes. Claude som grounding-modell krever kalibrering.
- Refleksjonen kan erklære en oppgave løst ut fra et gammelt resultat på skjermen.

## Plan

**v0 (forenklet):** Losen-sløyfen med hendelser og godkjenning av hvert steg, norsk «hva og hvorfor» i generatorens *Next Action*, TUI med én visning og en innstillingsfil. Claude i begge roller, bare macOS. Test av oppgave 1–2.

**v0.1:** `need_user` (spørsmål og overlevering), oppgave 3–5.

**Utsatt med vilje:** sluttbrukervindu, installasjonsfiler, OpenRouter-kobling, MCP, beskyttelse mot angrep via den delte kanalen (må være på plass før ekte brukere), sjekk mot tilgjengelighetstreet, skjermbilder i grensesnittet, ramme eller statusvindu som alltid ligger øverst, hjelp på avstand, Android og delegering.

**Åpent:** sjekk av varemerke og domene for «Losen», og lisens for egen kode før eventuell publisering.
