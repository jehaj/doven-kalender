# doven-kalender

Automatiske opslag på Facebook genereret med en LLM ud fra den offentlige IMU kalenderen.

Der er beskrevet mere om projektets struktur i ARCHITECTURE.md.

Tests kan køres med unittest modulet med

```bash
python3 -m unittest tests.py
```

## Opgaveliste

- [ ] Docker?
- [x] Secrets \
      Vi bruger ´.env´ filen til at gemme hemmeligheder. Det betyder, at man
      enten kan give programmet miljøvariabler, ellers læser den fra filen.
      Se `.env.example` for værdier den kan tage imod.
