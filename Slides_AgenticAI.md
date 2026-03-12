---
marp: true
theme: default
paginate: true
footer: ""
title: "Agentic AI with Python"
subtitle: ""
author: "Beispiel Projekt - Aktienanalyse"
date: "März 2026"
style: |
	section {
		font-family: "Avenir Next", "Segoe UI", "Trebuchet MS", sans-serif;
		font-size: 20px;
		line-height: 1.35;
		color: #102a43;
		background:
			radial-gradient(circle at 85% 10%, rgba(11, 102, 122, 0.14), transparent 28%),
			radial-gradient(circle at 10% 90%, rgba(245, 166, 35, 0.18), transparent 30%),
			linear-gradient(140deg, #f6fbff 0%, #eef5ff 45%, #f9fbf7 100%);
	}

	h1 {
		color: #0b667a;
		font-size: 1.65em;
		margin-bottom: 0.3em;
	}

	h2 {
		color: #243b53;
		font-size: 1.05em;
	}

	strong {
		color: #0f5132;
	}

	ul li,
	ol li {
		margin: 0.26em 0;
	}

	code {
		background: rgba(11, 102, 122, 0.1);
		color: #084c61;
		border-radius: 4px;
		padding: 0.08em 0.28em;
	}

	pre code {
		background: #f1f6fa;
		color: #102a43;
		border: 1px solid #d9e2ec;
	}

	section.lead {
		background:
			linear-gradient(135deg, rgba(11, 102, 122, 0.92) 0%, rgba(16, 42, 67, 0.94) 58%, rgba(15, 81, 50, 0.9) 100%);
		color: #f8fbff;
	}

	section.lead h1,
	section.lead h2,
	section.lead li {
		color: #f8fbff;
	}

	section::after {
		font-size: 0.52em;
		color: #486581;
	}

	    section.small {
        font-size: 16px;
    }

	    section.chapter {
        background: linear-gradient(135deg, #0b667a 0%, #102a43 100%);
        color: #f8fbff;
        text-align: center;
    }
    section.chapter h1, section.chapter h2, section.chapter p {
        color: #f8fbff;
    }

---


<!-- _class: lead -->

# Agentic AI (J. Vogt, 2026)

### Zielsetzung

- Fokus: Begriffliche Einordnung und technische Grundlagen
- Ergebnis: Sie können den Aufbau einer einfachen agentischen AI-Anwendung erklären und selbst eine App konzipieren.

 ### Content

 - AI Agenten und agentische Systeme
 - Autonomie
 - Umsetzung in Python



---


# AI Agenten

### Definition durch Unterscheidung von "One-Shot"-Abfragen 

- Das System können **wahrnehmen** (insbesondere über Tools), **handeln** (Tools nutzen), **Ergebnisse beobachten** und **nachsteuern**
- Kerncharakterisika: Iterationen und Tool-Use 


![width:900px](./rReact.svg)


---

<!-- _class: small -->

# Rolle von Tools

- Durch Tools kann das System:
  - Daten abrufen
  - Programme ausführen
  - Dateien ändern
  - APIs ansprechen
  - Wirkungen in der Umwelt erzeugen

---

<!-- _class: small -->

# Agentische AI Systeme..

- ..bestehen aus mehreren Agenten, die kollaborativ komplexe Ziele verfolgen.
- Dabei können einzelnen Agenten z.B. koordinieren und andere granularere Arbeitsschritte  ausführen.
- Grds. ist dabei ein hohes Maß an Autonomie möglich, worauf wir im Folgenden eingehen.
**Sum-Up:** Neben Iterationen und Tool-Use nun auch Orchestrierung / Zusammenspiel wichtig!

---
# Rollen der einzelnen Agenten

![width:900px](./orchestration.svg)

---
<!-- _class: small -->

# Autonomie..

- ..wird oft als zwingendes Charakterisikum von agentischen Workflows beschrieben.
- ABER: Konkrete Vorgaben zu Feedback-Loops können die Autonomie gegenüber klassischem One-Shot-Prompting in mancher Hinsicht reduzieren—zugunsten einer höheren Auditierbarkeit.
- Sinnvoll, **Autonomie differenziert zu betrachten** im Hinblick auf
    - Funktionale Autonomie in einem einzelnen Prozessschritt
    - Workflow-Autonomie (insb. in Bezug auf Evaluationsschritte) 

- Viel funktionale Autonomie heißt **nicht automatisch** viel Entscheidungsfreiheit. 

---
# Agentic AI Design Space

![width:750px](./autonomy_plot.svg)

<!-- ---

# Was ist nicht entscheidend?

- **Nicht nötig:** mehrere LLMs
- **Nicht nötig:** völlige Freiheit des Systems
- **Nicht nötig:** unkontrolliertes Handeln

Ein System kann **klar begrenzt** sein und trotzdem agentisch arbeiten,  
solange es **selbstständig im Loop** wahrnimmt, handelt und nachjustiert. -->

---

# Weitere in der Literatur diskutierte Charakteristika sind..

- ..die Lernfähigkeit und ein gemeinsames Gedächtnis eines agentischen Systems.
- Dabei können auch LLM-Gewichte angepasst werden (z.B. im Falle von Multi-Agent Reinforcement Learning (MARL)).
- Da das rechenintesiv ist werden aber oft lediglich neue Information / Erfahrungen. gespeichert. 
- Das kann anderem durch Datenbank-Tools ermöglicht werden. 
- Besonders wichtig ist aber die sequenzuielle Erweiterung des Kontexts erreicht (In-context Learning (ICL)).
---

# Multi-Agent In-context Learning

![width:750px](./multi_agent_loop.svg)

---


<!-- 
# Kurzdefinition für Studierende

- Agentic AI = ein LLM-basiertes System,
- das mit **Tools** arbeitet,
- **Aktionen** ausführt,
- **Ergebnisse beobachtet**
- und sein Verhalten **iterativ anpasst**

**Nicht zentral:** Anzahl der LLMs  
**Zentral:** **Loop + Toolnutzung + selbstständige Ausführung**

--- -->