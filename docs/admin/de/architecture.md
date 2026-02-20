# 2 Systemarchitektur, Komponenten und Datenverarbeitung

Dieses Kapitel beschreibt die grundlegenden architektonischen Prinzipien und das technische Gesamtdesign der Plattform LautrerWissen.

## 2.1 Architekturprinzipien und Systemdesign

Die Plattform ist als modulare, serviceorientierte Systemarchitektur konzipiert. Die einzelnen Funktionsbereiche sind logisch voneinander getrennt und werden in isolierten Docker-Containern betrieben. Dieses Design ermöglicht eine flexible Skalierung einzelner Dienste, eine klare Trennung von Verantwortlichkeiten sowie eine wartbare und erweiterbare Systemstruktur.

Die gewählte Architektur unterstützt insbesondere:
* Horizontale und vertikale Skalierbarkeit einzelner Dienste
* Hohe Wartbarkeit durch modulare Komponenten
* Entkoppelte Deployment- und Update-Prozesse
* Klare Trennung von Datenverarbeitung, Persistenz und Präsentation

Die technische Umsetzung basiert auf einem modernen, containerisierten Technologie-Stack, bestehend aus:

![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-316192?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/-Redis-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)
![Plausible](https://img.shields.io/badge/-Plausible-5850EC?logo=plausibleanalytics&logoColor=white)
![MQTT](https://img.shields.io/badge/-MQTT-660066?logo=eclipse-mosquitto&logoColor=white)

## 2.2 Komponentenübersicht 

Die nachfolgende Tabelle beschreibt die zentralen Komponenten des Systems, deren Rollen sowie ihre jeweilige Funktion innerhalb der Gesamtarchitektur.

| Service | Rolle | Beschreibung |
|----------|--------|--------------|
| **Backend (Django)** | Datenimport und -management | Bereitstellung einer REST-API, Administrationsoberfläche sowie Verwaltung von Datenpipelines, Frontend-Integration, Datenbeständen, Benutzerverwaltung und Monitoring |
| **Frontend** | Benutzeroberfläche | Öffentliche Webanwendung (separates Repository, siehe unten verlinkt) |
| **PostgreSQL** | Primäre Datenbank | Persistente Speicherung von Daten, Konfigurationen und Pipeline-Definitionen |
| **Redis** | Echtzeit-Sensorpuffer | In-Memory-Cache für aktuelle Sensordaten in Echtzeit |
| **MQTT Sensor Ingester** | Erfassung, Transformation und Speicherung von MQTT-Ereignissen | Verarbeitung eingehender MQTT-Nachrichten und Weiterleitung an Redis (Live-Daten) |
| **MQTT Fieldstrength Ingester** | Erfassung, Transformation und Speicherung von MQTT-Ereignissen | Verarbeitung von MQTT-Datenströmen und Speicherung in PostgreSQL (Signalanalyse und Diagnostik) |
| **Plausible Analytics** | DSGVO-konforme Analyse | Schlanke Analyse von Nutzungs- und Performance-Kennzahlen |
| **Health-Monitoring-Service** | Verfügbarkeits- und Anomalieüberwachung | Überprüfung der Systemkomponenten auf Funktionsfähigkeit sowie Erkennung von Log-Anomalien |

## 2.3 Systemworkflow und Datenverarbeitung

Die folgenden Punkte beschreiben den operativen Ablauf der Systemkomponenten sowie deren Zusammenspiel innerhalb der Gesamtarchitektur.

- **Datenpipelines**  
  Das Backend führt zeitgesteuerte ETL-Prozesse (Extract, Transform, Load) aus, um Daten aus externen Quellen wie APIs oder Open-Data-Portalen zu importieren, zu transformieren und strukturiert bereitzustellen.

- **Persistente Speicherung**  
  Importierte Daten sowie Systemkonfigurationen werden dauerhaft in **PostgreSQL** gespeichert und versioniert verwaltet.

- **API-Bereitstellung**  
  Das Django-Backend stellt standardisierte REST-Schnittstellen sowie eine Administrations- und Management-Oberfläche zur Verfügung.

- **Visualisierung**  
  Das Frontend ruft die bereitgestellten API-Daten ab und visualisiert diese in Dashboards sowie interaktiven Kartenansichten.

- **Monitoring und Observability**  
  **Plausible Analytics**, sowie ein Health-Monitoring-Service erfassen Kennzahlen, Logdaten und Systemzustände zur kontinuierlichen Überwachung und Analyse.

- **Echtzeitdatenverarbeitung**  
  MQTT-Ingester konsumieren Live-Sensordatenströme, verarbeiten diese und aktualisieren den Redis-Cache zur Bereitstellung aktueller Echtzeitdaten.

- **Client-Aktualisierung**  
  Über WebSocket-Verbindungen werden die in Redis zwischengespeicherten Live-Daten in Echtzeit an verbundene Web-Clients übertragen.


## 2.4 System-Komponenten – Detaillierte Beschreibung

Alle Kernservices der Plattform **LautrerWissen** sind als eigenständige Docker-Container implementiert. Jede Komponente besitzt eine eindeutig definierte fachliche und technische Verantwortung. Nachfolgend werden die zentralen Systemkomponenten strukturiert und technisch präzise beschrieben.

### 2.4.1 Backend – Django

**Technologie:** Python, Django, Django REST Framework  
**Container:** `core-backend`  
**Rolle im System:** Zentrale Koordinations- und Steuerungseinheit

Das Django-Backend bildet das funktionale Kernsystem von *LautrerWissen*. Es übernimmt sowohl die Datenverarbeitung als auch die Bereitstellung von APIs und Administrationsschnittstellen und ist die zentrale Koordinationsinstanz des Systems.


**Technische Verantwortung:**

- Verwaltung aller Datenmodelle (Smart-City-Daten, Konfiguration, Benutzer)
- Durchführung von ETL-Prozessen (Extract, Transform, Load) (`pipeline_manager`)
- Persistente Speicherung in PostgreSQL/PostGIS
- Bereitstellung einer REST-API unter `/api/`
- Bereitstellung von GeoJSON-Endpunkten unter `/api/geo/<modelname>`
- WebSocket-Endpunkte für Echtzeitübertragung von Sensordaten
- Benutzer- und Rechteverwaltung
- Konfigurationsverwaltung für Karten- und UI-Elemente

**Architektur innerhalb des Backends (Django Apps):**

| Django App         | Verantwortungsbereich |
|-------------------|-----------------------|
| `webapp`          | Core-Konfiguration, Routing, Settings |
| `lautrer_wissen`  | Fachlogik, Smart-City-Modelle, APIs |
| `pipeline_manager`| Definition & Ausführung von Import-Pipelines |
| `frontend_config` | Konfigurierbare Karten- und UI-Definition |
| `monitoring`      | Systemstatus, Log-Anzeige, Health-Views |

**REST-API :**

Über eine REST-API können Geodaten (Karte), Daten zu Veranstaltungen, Wahlen etc., sowie anwendungsspezifische Konfigurationsdaten zur Ansicht im Frontend abgfragt werden. Es sind ausschließlich lesende Zugriffe zugelassen.

- Basis-Endpoint: `/api/`
- Geo-Endpunkte (insb. für die Karte): `/api/geo/<modelname>`
- Ausgabeformate:
  - JSON
  - GeoJSON

Das Backend stellt die zentrale Integrationsschicht zwischen Datenquellen, Datenhaltung und Frontend dar.

---

### 2.4.2 Frontend – React / Next.js (PWA)

**Technologie:** React, Next.js  
**Container:** `core-frontend`  
**Rolle im System:** Präsentations- und Interaktionsschicht

Das Frontend stellt die öffentliche Benutzeroberfläche bereit. Es enthält keine Geschäftslogik, sondern konsumiert ausschließlich die vom Backend bereitgestellten APIs. Die Implementierung des Frontend befindet sich in einem separaten Repository.

**Technische Eigenschaften:**

- Implementierung als Next.js-Anwendung
- Deployment als Progressive Web Application (PWA)
- API-basierte Kommunikation mit dem Backend
- Darstellung von:
  - interaktiven Karten (GeoJSON-basiert)
  - Dashboards
  - Diagrammen
  - Echtzeit-Sensordaten
- WebSocket-Integration für Live-Updates

Durch die strikte Trennung von Backend und Frontend ist eine unabhängige Skalierung und Weiterentwicklung möglich.

---

### 2.4.3 PostgreSQL / PostGIS – Zentrale Datenbank

**Technologie:** PostgreSQL + PostGIS  
**Container:** `core-db`  
**Rolle im System:** Persistente Datenhaltung

PostgreSQL fungiert als primäre relationale Datenbank. Die PostGIS-Erweiterung ermöglicht die Verarbeitung und Speicherung georeferenzierter Daten.

**Gespeicherte Datenarten:**

- Importierte Smart-City-Daten
- Geometrien (Punkte, Linien, Polygone)
- Historische Sensordaten (z. B. Feldstärkemessungen)
- Pipeline-Konfigurationen
- Benutzerkonten und Rollen
- Systemkonfigurationen

**Technische Vorteile:**

- ACID-konforme Transaktionen
- Hohe Datenintegrität
- Native Geo-Operationen (Spatial Queries)
- Effiziente Indizierung (B-Tree, GIST, etc.)
- JSON/JSONB-Unterstützung

PostgreSQL bildet das persistente Rückgrat des Systems.

---

### 2.4.4 Redis – Realtime Cache Layer

**Technologie:** Redis  
**Container:** `core-cache`  
**Rolle im System:** Entkopplung und Beschleunigung von Echtzeitdaten

Redis wird als In-Memory-Datenspeicher eingesetzt, um aktuelle Sensordaten zwischenzuspeichern.

**Funktion im Gesamtsystem:**

- Zwischenspeicherung von MQTT-Sensordaten
- Bereitstellung schneller Lesezugriffe für WebSocket-Streams
- Reduzierung direkter Broker-Zugriffe
- Entkopplung von Echtzeit-Ingestion und Client-Auslieferung

**Architekturvorteil:**

Anstatt bei jeder Client-Anfrage eine Verbindung zum MQTT-Broker herzustellen, greift das Backend bzw. der WebSocket-Consumer direkt auf Redis zu. Dies reduziert:
- Latenz
- Broker-Last
- Netzwerk-Overhead

Redis speichert ausschließlich aktuelle Zustandsdaten (keine Langzeit-Historie).

---

### 2.4.5 MQTT Sensor Ingester

**Technologie:** Python, MQTT-Client  
**Container:** `core-mqtt-sensor-ingester`  
**Rolle im System:** Echtzeit-Ingestion von Sensordaten

Dieser Service verbindet sich mit dem MQTT-Broker und konsumiert konfigurierbare Topics (Sensorwerte für mehrere Queues).

**Verarbeitungsschritte:**

1. Subscription definierter MQTT-Topics (alle Queues die auf den regulären Ausdruck in `MQTT_TOPIC_SELECTOR` matchen) 
2. Empfang von JSON- oder LoRaWAN-Payloads
3. Validierung und Parsing der Daten
4. Transformation in internes Datenformat
5. Speicherung aktueller Werte in Redis

**Eigenschaften:**

- Event-Driven Architektur
- Keine persistente Speicherung
- Optimiert für niedrige Latenz
- Horizontal skalierbar

---

### 2.4.6 MQTT Fieldstrength Ingester

**Technologie:** Python, MQTT-Client  
**Container:** `core-mqtt-fieldstrength-ingester`  
**Rolle im System:** Persistente Speicherung diagnostischer Sensordaten

Dieser Service ist spezialisiert auf Feldstärke- bzw. Diagnosedaten.

**Unterschied zum Sensor Ingester:**

- Speicherung in PostgreSQL/PostGIS
- Historische Datenhaltung
- Grundlage für Analyse und Langzeitmonitoring z.b. der Berechnung der Feldstärke-Heatmap

**Verarbeitungsschritte:**

1. Subscription spezifischer Topics
2. Parsing und Validierung
3. Persistente Speicherung in der Datenbank

---

### 2.4.7 Health Monitor Service

**Technologie:** Custom Service  
**Container:** `sidecar-health-monitor`  
**Rolle im System:** Überwachung der Systemverfügbarkeit und Logs.

Der Health Monitor überprüft regelmäßig den Zustand aller Docker-Kernkomponenten. Was werden regelmäßig Analysen des Access-Logs (z.B. des Nginx Reverse-Proxy Servers) erstellt und in der Adminansicht integriert.

**Überwachungsmechanismen:**

- TCP-Port-Checks (PostgreSQL, Redis, Backend, Frontend)
- API-Health-Endpunkte
- Prüfung von Heartbeat-Dateien der MQTT-Services
- Regelmäßige Log-Analyse des Access-Logs

Ziel ist die frühzeitige Erkennung von:

- Dienstunterbrechungen
- Kommunikationsproblemen
- Ingestion-Ausfällen

Der Health Monitor Service ist vollständig von den Kernkomponenten getrennt und beeinflusst nicht die Performance des Backends. Es wird ausschließlich und optional zum System-Monitoring eingesetzt.

---

### 2.4.8 Plausible Analytics – Web-Analytics-Infrastruktur

**Rolle im System:** DSGVO-konforme Nutzungsanalyse  
**Deployment:** Eigene Container-Umgebung

Plausible Analytics wird self-hosted betrieben und besteht aus drei klar getrennten Komponenten.

#### 1. Plausible-Analytics (Application Service)

- Implementiert in Elixir (Phoenix Framework)
- Nimmt Tracking-Events über HTTP entgegen
- Aggregiert Metriken
- Stellt das Analytics-Dashboard bereit
- Bietet API-Endpunkte für Statistik-Abfragen

#### 2. PlausibleDB (PostgreSQL)

- Speicherung von:
  - Benutzerkonten
  - Websites
  - Konfigurationen
  - API-Tokens
  - Rollen & Berechtigungen
- Enthält keine hochvolumigen Eventdaten

#### 3. Plausible EventsDB (ClickHouse)

- Hochperformante Event-Datenbank
- Speicherung von:
  - Pageviews
  - Referrer-Informationen
  - Conversion-Events
  - Geräte- und Browserinformationen
- Optimiert für Zeitreihen-Analysen
- Sehr schnelle Aggregationen bei großen Datenmengen

**Datenschutz-Eigenschaften:**

- Keine Cookies
- Keine personenbezogenen Identifikatoren
- IP-Anonymisierung
- Self-Hosted-Betrieb

Plausible ist vollständig von den Kernkomponenten getrennt und beeinflusst nicht die Performance des Backends.

---

### 2.4.9 Reverse Proxy (Empfohlen)

**Typische Technologie:** NGINX oder Traefik  
**Rolle:** Edge-Service / Reverse Proxy

Nicht Bestandteil des Kernsystems, jedoch empfohlen für produktive Deployments, insbesondere für das Routing von Requests an das Backend bzw. Frontend. 

**Aufgaben:**

- TLS-Terminierung
- HTTPS-Erzwingung
- Routing zu Backend / Frontend
- Security-Header
- Caching, Bereitstellung von statischen Daten (Bilder etc.)

Die konkrete Implementierung ist abhängig vom jeweiligen Deployment-Szenario.