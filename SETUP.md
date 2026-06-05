# Agents Hub — Setup

## 1. Configurar API Key

Copia el archivo de ejemplo y agrega tu key:

```
cp .env.example .env
```

Edita `.env` y pon tu `ANTHROPIC_API_KEY`.

---

## 2. Python (Core — recomendado para empezar)

```bash
cd python
pip install -r requirements.txt
py -3.12 main.py
```

Elige el modo (investigación / coding / automatización) y describe tu tarea.

---

## 3. JavaScript

```bash
cd js
npm install

# Usar Claude directamente:
node tools/api_client.js research "inteligencia artificial en 2025"
node tools/api_client.js code "función que ordena una lista en Python"

# Scraping:
node tools/scraper.js https://example.com
```

---

## 4. Go (Servidor HTTP)

```bash
cd go
go mod tidy
go run server/main.go
```

El servidor corre en `http://localhost:8080`.

Endpoints:
- `GET  /health` — estado del servidor
- `POST /ask` — pregunta a Claude: `{"prompt": "tu pregunta"}`
- `POST /automate` — tarea de automatización: `{"prompt": "automatiza X"}`

---

## 5. Kotlin

```bash
cd kotlin
./gradlew run --args="research inteligencia artificial"
./gradlew run --args="code función fibonacci en Kotlin"
./gradlew run --args="automate backup de archivos"
```

---

## Arquitectura

```
Python  ──► Core de agentes (CrewAI) — orquestación completa
JS      ──► Web scraping + CLI rápido con Claude
Go      ──► Microservicio HTTP de alta velocidad
Kotlin  ──► Integración JVM / Android
```
