# doven-kalender

Automatiske opslag på Facebook genereret med en LLM ud fra den offentlige IMU kalenderen.

Der er beskrevet mere om projektets struktur i ARCHITECTURE.md.

## LLM arkitektur

Projektet bruger nu et delt LLM-lag i `generator.py`, så både parser og generator
kan bruge samme interface.

- `GeneralLLM`: Abstrakt interface for både tekst og struktureret output.
- `Generator`: Tynd wrapper der bruger en `GeneralLLM` implementation.
- `EventParser` i `parser.py`: Bruger samme `GeneralLLM` interface.

### Structured output med Pydantic

Alle LLM-kald kan modtage en valgfri `response_model` (Pydantic-model):

- Uden `response_model` returneres `str`.
- Med `response_model` returneres en valideret Pydantic-instans.

### Environment variables

- `GOOGLE_API_KEY`: API key til kalender extraction.
- `DOVEN_LLM_PROVIDER`: `gemini` eller `mistral` (default: `gemini`).
- `GOOGLE_CALENDAR_ID`: Kalender-id (uden `@group.calendar.google.com`).
- `DOCS_COOKIE`: Browser cookie value needed to download the protected PU ODT export.

### PU pipeline

The calendar-to-JSON pipeline lives under [scripts/](scripts/) and is exposed as a console command through [pyproject.toml](pyproject.toml).

Run it with:

```bash
uv run pu-pipeline maj juni
```

It reads `DOCS_DOCUMENT_URL` from [.env](.env), downloads the ODT export, writes the intermediate CSV, then produces the emoji-enriched JSON output.

## Opgaveliste

- [ ] Docker?
- [ ] Secrets (environment?)
