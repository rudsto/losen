# Losen – for Claude Code

KI-assistent som styrer datamaskinen synlig, forklart og stoppbart, bygget på Agent S3. Les README, `docs/konsept.md` og `docs/plan.md` før du endrer noe.

## Regler

- Arbeid i grener (`iter-1.1/...`, `fix/...`, `docs/...`), aldri direkte på `main`. Én iterasjon per pull request.
- Claude committer bare lokalt. Utvikleren pusher og lager pull requests selv.
- S3-filene i `.venv` endres aldri. Tilpasninger ligger i `src/losen/s3_adapt.py`.
- Versjonene av `gui-agents` og `anthropic` er låst. Oppgradering er en egen oppgave.
- Ingen nøkler, logger eller skjermbilder i repoet. `logs/` er ignorert.
- Kjør aldri `losen` eller `losen-s3` mot den ekte skjermen uten at utvikleren ber om det.
- Beslutninger skrives i `docs/konsept.md`, planendringer i `docs/plan.md`, funn fra bruk i `docs/erfaringer.md`.

## Kommandoer (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe tests\run_checks.py          # nivå 1
.\.venv\Scripts\python.exe tests\run_checks.py --api    # nivå 1 + 2, krever ANTHROPIC_API_KEY
```

Testnivå 1 skal være grønt før hver commit.
