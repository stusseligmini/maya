# 🚀 Maya AI System - Utviklerguide

Denne guiden gir oversikt over den konsoliderte Maya AI-systemarkitekturen og hvordan du kan jobbe med kodebasen.

## Systemarkitektur

Maya AI er et innholdsoptimalisseringssystem som bruker AI for å analysere, generere og optimalisere innhold for ulike sosiale medieplattformer. Systemet består av følgende hovedkomponenter:

```
maya/
  ├── api/            # API-komponenter
  ├── services/       # Tjenestelaget
  ├── core/           # Kjernefunksjonalitet
  ├── worker/         # Bakgrunnsarbeidere
  ├── monitoring/     # Overvåkingsverktøy
  └── utils/          # Hjelperutiner
```

## Komme i gang

### Forutsetninger
- Python 3.12+
- Docker og Docker Compose
- PostgreSQL
- Redis

### Installasjon

1. **Klon repositoriet**
   ```bash
   git clone https://github.com/yourusername/maya.git
   cd maya
   ```

2. **Sett opp virtuelt miljø og installer avhengigheter**
   ```bash
   python -m venv venv
   source venv/bin/activate  # På Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For utviklingsverktøy
   ```

3. **Konfigurer miljøvariabler**
   Kopier eksempelkonfigurasjonsfilen og juster etter behov:
   ```bash
   cp config/dev.env .env
   ```

4. **Initialiser databasen**
   ```bash
   python maya_run.py init-db
   ```

5. **Start API-serveren**
   ```bash
   python maya_run.py api --reload
   ```

6. **Start arbeideren (i et annet terminalvindu)**
   ```bash
   python maya_run.py worker
   ```

## Utvikling

### Kjøre tester
```bash
pytest
```

### API-dokumentasjon
Når API-serveren kjører, besøk `http://localhost:8000/docs` for interaktiv API-dokumentasjon.

### Docker-utvikling
For å kjøre hele systemet med Docker:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

## Kjernekomponenter

### API (`maya/api/`)
APIet er bygget med FastAPI og definerer alle endepunkter for systemet. Det bruker tjenestelaget for å utføre operasjoner.

### Tjenester (`maya/services/`)
Tjenestelaget implementerer forretningslogikken og integrerer AI-modeller, innholdsprosessering og plattformoptimalisering.

### Kjerne (`maya/core/`)
Inneholder grunnleggende funksjonalitet som brukes på tvers av systemet, inkludert modeller, konfigurasjon og unntakshåndtering.

### Arbeider (`maya/worker/`)
Håndterer asynkrone og bakgrunnsprosesser som innholdsgenerering, optimalisering og planlagte oppgaver.

### Overvåking (`maya/monitoring/`)
Implementerer Prometheus-metrikker og helsesjekker for systemet.

### Verktøy (`maya/utils/`)
Inneholder hjelpeverktøy for Docker-konfigurasjon, CI/CD-oppsett og andre generelle verktøy.

## Viktige konsepter

### Innholdsprosessering
Maya bruker en pipeline for innholdsprosessering som utfører flere trinn:
1. **Analyse**: Bruk av AI-modeller for å analysere innholdet
2. **Optimalisering**: Tilpasning av innholdet til ulike plattformer
3. **Validering**: Sjekke innholdet mot plattformspesifikke regler
4. **Anbefaling**: Generere anbefalinger for forbedringer

### AI-modeller
Systemet støtter flere AI-modellintegrasjoner:
- OpenAI GPT-modeller
- HuggingFace Transformers
- Lokale modeller

### Plattformstøtte
Maya optimaliserer innhold for følgende plattformer:
- Twitter
- Instagram
- TikTok
- Facebook
- LinkedIn

## Bidrag

1. Opprett en fork av repositoriet
2. Opprett en funksjonsbranch (`git checkout -b feature/amazing-feature`)
3. Gjør endringer og legg til tester
4. Commit endringene (`git commit -m 'Add amazing feature'`)
5. Push til branchen (`git push origin feature/amazing-feature`)
6. Åpne en Pull Request

## Lisens

Dette prosjektet er lisensiert under [Din Lisens] - se LICENSE-filen for detaljer.
