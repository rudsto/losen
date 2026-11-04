# Erfaringer fra egen bruk (del 1)

Her samles det som fungerer og ikke fungerer når Losen brukes. Funnene er grunnlaget for del 2. Én rad per funn.

| Dato | Funn | Tiltak |
|---|---|---|
| 2026-11-03 | Anthropic-SDK 2.4.0 tar ikke imot `temperature`, men S3 sender den alltid. | Rettet i `s3_adapt`. |
| 2026-11-03 | S3-prompten hadde et hardkodet OSWorld-passord og en invitasjon til `sudo` (regel 7). | Fjernet i `s3_adapt`. |
| 2026-11-04 | Claude kan svare med en tenkeblokk først. S3 leser bare `content[0].text`. | Rettet i `s3_adapt`: tekstblokker legges først. |
| 2026-11-04 | Når ett svar feiler, legger S3 et tomt svar i historikken, og neste kall avvises. | Åpent. |
| 2026-11-04 | Refleksjonen erklærte Kalkulator-oppgaven løst ut fra et gammelt resultat på skjermen. | Nullstill før hver test. Ekstern sjekk i evalueringen (del 2). |
| 2026-11-04 | `open` bruker Spotlight (⌘ + mellomrom), selv når hurtigtaster er av. | Del 2: synlig åpning eller tydelig forvarsel. |
| 2026-11-04 | `type` limer inn med ⌘V, og brukerens utklippstavle overskrives. | Del 2: synlig skriving. |
