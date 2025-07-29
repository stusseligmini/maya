# 📊 Maya AI System - Brukerguide

Denne guiden forklarer hvordan du bruker det konsoliderte Maya AI-systemet for å optimalisere innhold for sosiale medier.

## Introduksjon

Maya AI er et innholdsoptimaliseringssystem som bruker kunstig intelligens for å analysere, generere og forbedre innhold for ulike sosiale medieplattformer. Systemet kan hjelpe deg med å:

- Analysere eksisterende innhold for engasjementspotensial
- Optimalisere innhold for spesifikke plattformer (Twitter, Instagram, TikTok, etc.)
- Generere engasjerende innhold basert på dine inndata
- Moderere innhold for sikkerhetssjekk
- Beregne beste publiseringstider

## Kom i gang

### Tilgang til systemet
Maya AI kan brukes gjennom:
1. Web-grensesnitt: Besøk Maya-dashbordet
2. API: Integrer Maya med dine eksisterende systemer
3. Kommandolinje: Bruk Maya CLI for automatisering

### Autentisering
For å bruke systemet må du ha en gyldig brukerkonto. Kontakt systemadministratoren din for å få tilgang.

## Bruksscenarier

### 1. Innholdsanalyse

Slik analyserer du eksisterende innhold:

1. Last opp innholdet ditt (tekst, bilde eller video)
2. Velg "Analyser" fra handlingsmenyen
3. Systemet vil gi deg en analyse av:
   - Sentimentanalyse (positiv/negativ/nøytral)
   - Engasjementspotensial
   - Nøkkeltemaer og anbefalte hashtags
   - Forbedringsforslag

### 2. Innholdsoptimalisering

For å optimalisere innhold for en spesifikk plattform:

1. Last opp innholdet ditt
2. Velg "Optimiser" fra handlingsmenyen
3. Velg målplattform(er) (Twitter, Instagram, TikTok, etc.)
4. Systemet vil optimalisere innholdet ditt ved å:
   - Justere teksten for plattformens begrensninger
   - Velge optimale hashtags
   - Foreslå bildestørrelser og formater
   - Gi plattformspesifikke anbefalinger

### 3. Innholdsgenerering

For å generere nytt innhold:

1. Gå til "Generer" i navigasjonsmenyen
2. Skriv inn et tema eller emne
3. Velg målplattform(er)
4. Systemet vil generere innhold som er optimalisert for de valgte plattformene

## API-bruk

Maya AI tilbyr et omfattende REST API for integrasjon med andre systemer.

### Autentisering

```bash
curl -X POST "https://your-maya-instance.com/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

Dette vil returnere en JWT-token som må inkluderes i alle påfølgende forespørsler.

### Eksempel: Innholdsanalyse

```bash
curl -X POST "https://your-maya-instance.com/api/v1/ai/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Dette er mitt eksempelinnhold som skal analyseres."}'
```

### Eksempel: Innholdsoptimalisering

```bash
curl -X POST "https://your-maya-instance.com/api/v1/content/process" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_data": {
      "text": "Dette er mitt innhold",
      "media_urls": ["http://example.com/image.jpg"],
      "hashtags": ["AI", "innhold", "sosiale medier"]
    },
    "target_platforms": ["twitter", "instagram"]
  }'
```

## Plattformspesifikke begrensninger

Maya AI tar hensyn til følgende plattformspesifikke begrensninger:

| Plattform | Tekstlengde | Bildestørrelser      | Videovarighet | Hashtags |
|-----------|-------------|----------------------|---------------|----------|
| Twitter   | 280 tegn    | 1200x675px           | 140 sek       | 3-5      |
| Instagram | 2200 tegn   | 1080x1080px, 1080x1350px | 60 sek     | Opptil 30 |
| TikTok    | 150 tegn    | N/A                  | 180 sek       | 3-5      |
| Facebook  | 63206 tegn  | 1200x630px           | 240 sek       | Ubegrenset |
| LinkedIn  | 3000 tegn   | 1200x627px           | 600 sek       | 3-5      |

## Ofte stilte spørsmål

### Hvilke filformater støttes?
Maya støtter følgende formater:
- Bilder: JPEG, PNG, WebP, GIF
- Video: MP4, MOV, AVI, WebM
- Tekst: Ren tekst, Markdown, HTML

### Hvordan beregnes engasjementspotensial?
Engasjementspotensial beregnes ved å analysere flere faktorer, inkludert:
- Sentiment og tone
- Relevans for målplattform
- Historisk engasjementsdata
- Innholdslengde og -format
- Bruk av hashtags og nøkkelord

### Er det begrensninger på API-bruk?
Ja, API-bruk er begrenset basert på abonnementsnivå. Standardbegrensninger er:
- Gratis: 100 forespørsler per dag
- Standard: 1000 forespørsler per dag
- Premium: 10000 forespørsler per dag

## Kontakt og støtte

For spørsmål eller støtte, kontakt oss på:
- E-post: support@maya-ai.com
- Hjelpesenter: https://help.maya-ai.com
