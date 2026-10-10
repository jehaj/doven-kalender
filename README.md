# doven-kalender

Generering af opslag ud fra den offentlige IMU-kalender ved hjælp af en LLM.

> **Status på Facebook-integration:**
> Slutmålet for projektet er automatiske opslag på Facebook genereret ud fra kalenderen. Direkte Facebook-opslag er dog i øjeblikket sat på pause, da det ikke er umiddelbart gennemførligt at poste automatisk i en Facebook-gruppe med en bot, og en holdbar løsning er endnu ikke fastlagt.
> En retning der arbejdes hen imod er i stedet at maile det genererede opslag til en person (f.eks. mødelederen), som kan verificere indholdet og selv foretage opslaget på Facebook.

Der er beskrevet mere om projektets struktur i ARCHITECTURE.md.

Tests kan køres med unittest modulet med:

```bash
python3 -m unittest discover tests
```

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
- [x] Secrets \
      Vi bruger `.env` filen til at gemme hemmeligheder. Det betyder, at man
      enten kan give programmet miljøvariabler, ellers læser den fra filen.
      Se `.env.example` for værdier den kan tage imod.
- [ ] Poster-løsning (e-mail verifikation før manuel/assisteret Facebook-deling)
