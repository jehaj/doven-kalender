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
- `DOVEN_LLM_PROVIDER`: `google`, `openai` eller `mistral` (default: `openai`).
- `GOOGLE_CALENDAR_ID`: Kalender-id (uden `@group.calendar.google.com`).

## Opgaveliste

- [ ] Docker?
- [ ] Secrets (environment?)
