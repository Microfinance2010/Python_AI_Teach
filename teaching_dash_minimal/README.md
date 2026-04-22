# teaching_dash_minimal

Mini-Lehrprojekt fuer Studierende mit:

- SEC Company Facts API
- einfachen Bewertungsmetriken
- RAG auf 10-K Filings
- einer kleinen Dash-Oberflaeche

## Dateien in diesem Ordner

- `teaching_dash_minimal.ipynb`: das eigentliche Lehr-Notebook
- `teaching_dash_minimal_utils.py`: lokale Hilfsfunktionen fuer dieses Notebook
- `requirements.txt`: benoetigte Python-Pakete

## Installation

Am besten in einem frischen virtuellen Environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Start

```bash
jupyter lab teaching_dash_minimal.ipynb
```

## Architektur

Dieses Mini-Projekt trennt drei Ebenen:

1. `main_api` ist ein eigenstaendiges, wiederverwendbares Paket fuer generische SEC-API-Funktionen.
2. `teaching_dash_minimal_utils.py` enthaelt notebook-spezifische Hilfsfunktionen.
3. Das Notebook zeigt die Orchestrierung, Erklaerung und Nutzung.

## Hinweis zu `main_api`

`main_api` wird nicht mehr als lokale Datei in diesem Unterordner erwartet, sondern als installiertes Paket.
Die Installation erfolgt ueber den GitHub-Eintrag in `requirements.txt`.

Fuer stabile Lehrveranstaltungen sollte dort immer eine feste Version oder ein Tag verwendet werden.
