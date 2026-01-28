# SupplyScore: Analyse der regionalen Bankenversorgung

Dieses Projekt analysiert die Versorgungssituation von Bankdienstleistungen in verschiedenen Städten. Es berechnet Versorgungsindizes, vergleicht den Status „Vorher“ vs. „Nachher“ und visualisiert die Ergebnisse in Bubble-Plots.

## 📄 Projektbeschreibung
Ziel ist es, strukturelle Unterschiede in der regionalen Versorgung sichtbar zu machen. Das Skript verarbeitet Städtedaten, berechnet Scores für Über- oder Unterversorgung und stellt diese grafisch dar.

Besonderer Fokus liegt auf der **Lesbarkeit der Grafiken**: Durch Algorithmen zur Textpositionierung wird verhindert, dass sich Städtenamen in den Diagrammen überlappen.

## 🧮 Kriterien & Marktvolumen
Die Analyse basiert auf einer spezifischen Definition des Marktvolumens, angepasst auf die regionale Bankenstruktur:

* **Sachlich:** Betrachtet wird das Angebot an stationären Bankdienstleistungen.
* **Räumlich:** Vergleich auf Ebene einzelner Städte/Kommunen.
* **Marktvolumen (Potenzial):** Die **Einwohnerzahl** der jeweiligen Stadt dient als Indikator für das maximale Nachfragepotenzial. In den Visualisierungen wird dies durch die **Größe der Blasen (Bubbles)** dargestellt.
* **Scoring-Logik:**
    *  Gebiete mit hohem Einwohnerpotenzial bei geringer Bankendichte.
    *  Gebiete mit Sättigungstendenzen (sehr viele Banken pro Einwohner).

## 🛠 Technologien
Das Projekt wurde mit Python 3 umgesetzt und nutzt folgende Bibliotheken:
* **pandas:** Datenaufbereitung und -analyse.
* **matplotlib:** Erstellung der Scatter- und Bubble-Plots.
* **adjustText:** Automatische Optimierung der Textbeschriftungen im Plot.
* **numpy:** Mathematische Berechnungen.

## 🚀 Installation & Nutzung

1.  **Voraussetzungen**

    Stelle sicher, dass Python installiert ist.

2.  **Abhängigkeiten installieren**

    Alle notwendigen Pakete sind in der `requirements.txt` gelistet. Installiere sie mit:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Projekt ausführen**
    Starte die Analyse mit:
    ```bash
    python main.py
    ```


## 📂 Dateistruktur
* `main.py` – Hauptskript (Berechnung & Plotting)
* `requirements.txt` – Liste der Python-Abhängigkeiten
* `data/` – Ordner für die Eingabedaten (CSV/Excel)
* `README.md` – Diese Dokumentation