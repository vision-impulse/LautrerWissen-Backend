# Admin-Handbuch – LautrerWissen

## 1. Einleitung

Dieses Administrationshandbuch beschreibt die technischen, betrieblichen und organisatorischen Grundlagen der Webanwendung **LautrerWissen**.  Es dient als Referenz für Installation, Konfiguration, Betrieb, Wartung sowie die kontinuierliche Weiterentwicklung des Systems.

LautrerWissen ist eine modulare Smart-City-Plattform zur Erfassung, Verarbeitung, Speicherung und Visualisierung heterogener Datenquellen. Das System stellt ein zentrales Daten-Backend mit integrierter Monitoring- und Analyseinfrastruktur bereit und unterstützt damit datengetriebene urbane Informationssysteme.

## 1.1 Überblick

Die Plattform LautrerWissen aggregiert und verarbeitet Daten aus unterschiedlichen externen und internen Quellen, darunter:

- Geodaten (z. B. OpenStreetMap, kommunale Geodatenportale, externe Schnittstellen)  
- Offene Verwaltungs- und Open-Data-Portale  
- Wissensquellen wie Wikipedia  
- Veranstaltungs- und Eventdaten  
- IoT- und Sensordaten (z. B. LoRaWAN)  
- Weitere projekt- oder kommunenbezogene Fachverfahren  

Die Datenverarbeitung erfolgt in einem standardisierten Ablauf:

1. **Automatisierter Import** über definierte Datenpipelines  
2. **Transformation und Normalisierung** zur Vereinheitlichung der Datenstruktur  
3. **Persistente Speicherung** in einer zentralen Datenbank  
4. **Bereitstellung und Visualisierung** über Weboberflächen und APIs  

Das System fungiert somit als konsolidiertes Smart-City-Datenbackend mit integrierter Monitoring-, Analyse- und Visualisierungsfunktion.

## 1.2 Zweck und Geltungsbereich dieses Handbuchs

Dieses Dokument definiert die administrativen und technischen Rahmenbedingungen für einen sicheren, stabilen und wartbaren Produktivbetrieb.

Das Handbuch unterstützt insbesondere bei:

- dem Verständnis der Systemarchitektur und Komponentenstruktur  
- der Erstinstallation und Inbetriebnahme  
- der Konfiguration und Anpassung von Systemdiensten  
- dem laufenden Betrieb inklusive Monitoring und Logging  
- Wartungsarbeiten, Updates und Backup-Strategien  
- Fehleranalyse und strukturiertem Troubleshooting  

Detaillierte Anleitungen und technische Tiefenbeschreibungen befinden sich in den jeweiligen Unterkapiteln dieses Handbuchs.

## 1.3 Zielgruppe

Dieses Administrationshandbuch richtet sich an folgende Rollen:

### Systemadministratoren / Fachadministratoren
- mit fundierten Linux- und Serverkenntnissen  
- verantwortlich für Installation, Konfiguration und Betrieb  
- zuständig für Monitoring, Sicherheit, Backup-Strategien und Updates  

### Entwickler / Systemintegratoren
- verantwortlich für Backend-, Frontend- oder Infrastrukturkomponenten  
- zuständig für Weiterentwicklung, Testing und Qualitätssicherung  
- beteiligt an Architekturentscheidungen und Systemerweiterungen  

## 1.4 Aufbau des Handbuchs

Die weiteren Kapitel dieses Dokuments sind thematisch strukturiert und behandeln unter anderem:

* [`Systemarchitektur und Komponentenübersicht`](./architecture.md)   
* [`Installations- und Deploymentprozesse`](./installation.md) 
* [`Konfigurationsrichtlinien und Umgebungsvariablen`](./configuration.md) 
* [`Betrieb, Wartung, Updates und Troubleshooting`](./troubleshooting.md) 

Jedes Kapitel ist in sich abgeschlossen und kann bei Bedarf gezielt als Referenz für den jeweiligen Aufgabenbereich verwendet werden.
