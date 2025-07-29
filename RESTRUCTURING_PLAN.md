# 🔄 Maya AI Restrukturering Plan

## 1. Konsolidering av Kodebase

### Nåværende problemer:
- Duplisert funksjonalitet mellom `/api` og `/app/api`
- Fragmentert modellstruktur på tvers av `/app/models` og `/database/models`
- Uklart grensesnitt mellom `maya/` og `/app` modulene
- Mange små filer som gjør prosjektet vanskelig å navigere

### Ny foreslått struktur:
```
maya/
  ├── api/            # All API-funksjonalitet
  │   ├── auth.py     # Autentisering
  │   ├── content.py  # Innholdshåndtering
  │   └── integrations/ # Eksterne integrasjoner
  ├── core/           # Kjernefunksjonalitet
  │   ├── models.py   # Alle datamodeller samlet
  │   ├── services.py # Tjenester (AI, prosessering)
  │   └── config.py   # Konfigurasjon
  ├── worker/         # Bakgrunnsarbeid
  │   ├── tasks.py    # Celery-oppgaver
  │   └── scheduler.py # Planlegger
  └── utils/          # Felles verktøy
      ├── security.py # Sikkerhetsfunksjoner
      └── logging.py  # Loggingsverktøy
```

## 2. Integrasjonsprioriteter:
1. **API & Datalag**: Forene modeller og APIer
2. **Arbeidsflyt**: Koble innholdsgenerering med modereringsarbeidere
3. **Monitoring**: Integrere Prometheus-metrikker med applikasjonskode

## 3. Forbedringer:
- Implementere asynkron filhåndtering for bedre ytelse
- Legge til helsesjekk for alle tjenester
- Implementere robust feilhåndtering
- Forbedre Docker-oppsett med multi-stage bygging
- Konfigurere CI/CD med GitHub Actions

## 4. Leveransefaser:
1. **Konsolidering**: Forene duplisert kode
2. **Integrasjon**: Koble komponenter
3. **Forbedring**: Implementere nye funksjoner
4. **Dokumentasjon**: Oppdatere README og guides
