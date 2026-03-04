# 3 Konfiguration und Umgebungsvariablen

Dieses Kapitel beschreibt die grundlegenden Konfigurationsmechanismen des Systems sowie den strukturierten Umgang mit Umgebungsvariablen. Es erfolgt eine klare Trennung zwischen:
- Laufzeit-Konfiguration
- Sensitiven Daten (Secrets)
- Initialen Anwendungsdaten

Die Konfiguration erfolgt primär über `.env`-Dateien in Kombination mit Docker Compose. Dieses Vorgehen ermöglicht reproduzierbare Deployments, eine saubere Trennung von Code und Konfiguration sowie eine klare Unterscheidung zwischen Entwicklungs- und Produktionsumgebungen.

## 3.1 Umgebungsvariablen

Alle Systemkomponenten (Backend, Frontend, Datenbank, Cache, Reverse Proxy usw.) werden über Umgebungsvariablen konfiguriert. Dieser Ansatz bietet folgende Vorteile:
- Trennung von Konfiguration und Quellcode  
- Flexible Anpassung je nach Umgebung (prod / dev) 
- CI/CD-Kompatibilität  
- Erhöhte Wartbarkeit und Transparenz  

In den `.env`-Dateien werden **keine sensitiven Zugangsdaten** gespeichert. Diese werden gesondert verwaltet (siehe Abschnitt 3.2).


## 3.1.1 Verwendung von `.env`-Dateien

Die Konfiguration wird über `.env`-Dateien gesteuert, die von Docker Compose eingelesen werden.

### Entwicklungsumgebung

```bash
cp .env.example .env
```

Die Datei `.env` wird automatisch von Docker Compose geladen.

### Produktionsumgebung

```bash
cp .env.example .env.prod
```

Für Produktionsdeployments wird die Datei explizit übergeben, da ausgewählte Umgebungsvariablen ebenfalls als build parameter an next.js (core-frontend Komponente) übergeben werden:

```bash
docker compose -f compose.yaml -f docker/compose/compose.prod.yaml --env-file .env.prod up --build -d
```

Dadurch wird sichergestellt, dass keine Entwicklungsparameter unbeabsichtigt in produktive Deployments gelangen.

## 3.1.2 Beispielhafte `.env.example`

Die folgende Datei dient als Vorlage und enthält kommentierte Beschreibungen aller Variablen.

```.env.example
############################################
# Basis-Verzeichnisse
############################################

# Konfigurationsverzeichnis der Anwendung
APP_CONFIG_DIR=/config

# Persistente Anwendungsdaten
APP_DATA_DIR=/appdata

# Log-Verzeichnis
APP_LOG_DIR=./logs

# Persistente Datenbankdaten
APP_DATA_DIR_DB=/appdata/components/db

############################################
# Docker-Komponenten (Hostnamen & Ports)
# (Default Werte können angepasst werden)
############################################

# Redis Cache
REDIS_HOST=redis
REDIS_PORT=6379

# Datenbankverbindung
DATABASE_HOST=core-database
DATABASE_PORT=5432

# Backend-Service Port (z.B. 8000)
DJANGO_BACKEND_PORT=

# Frontend-Service Port (z.B. 3000)
FRONTEND_PORT=

############################################
# Infos zu externen Datenquellen im Frontend 
# (Lediglich zur Info/Link unter 'Datenquelle')
############################################

# Info-URL zu dem Geodatenportal
NEXT_PUBLIC_URL_GEOPORTAL=

# Info-URL zu dem Veranstaltungskalender
NEXT_PUBLIC_URL_EVENT_CALENDAR=

# Info-URL zu dem Ratsinformationssystem
NEXT_PUBLIC_URL_RIS_CALENDAR=

# Info-URL zum WGA Kalender
NEXT_PUBLIC_URL_WGA_CALENDAR=

############################################
# MQTT-Konfiguration
############################################

# Adresse/Host des Brokers
MQTT_BROKER=

# Port des MQTT-Brokers
MQTT_PORT=

############################################
# Konfiguration zum Monitoring
############################################

# Überprüfung der Docker Komponenten (Default: 600) 
DOCKER_CHECK_INTERVAL_SECONDS=

# Anaylse des Nginx-Logs (Default: 3600) 
LOG_ANALYSIS_INTERVAL_SECONDS=

############################################
# Backend-spezifische Konfiguration
# Unterschiedlich für prod und dev!
# (Siehe Django Dokumentation für Details)
############################################

# Betriebsmodus (dev oder prod)
DJANGO_ENV=

# Öffentliche URL des Frontends
DJANGO_FRONTEND_URL=changeme

# Aktivierung interner Scheduler-Prozesse (True/False)
# Verwendet für cron jobs -> für dev ggf. False
DJANGO_SCHEDULER_ENABLED=

# Security: Zulässige Hosts (Comma-separated)
DJANGO_ALLOWED_HOSTS=changeme,

# Security: CORS-Konfiguration
DJANGO_CORS_ALLOWED_ORIGINS=changeme
DJANGO_CSRF_TRUSTED_ORIGINS=changeme

# Security: Cookie-Domains
DJANGO_SESSION_COOKIE_DOMAIN=changeme
DJANGO_CSRF_COOKIE_DOMAIN=changeme

############################################
# E-Mail-Konfiguration
############################################

# SMTP-Server (Sender E-Mail Server Host)
DJANGO_EMAIL_HOST=

# SMTP-Port (Sender E-Mail Server Port)
DJANGO_EMAIL_PORT=

# Empfänger für Systembenachrichtigungen 
# (Format: KÜRZEL:EMAIL-ADRESSE,KÜRZEL2:EMAIL-ADRESSE2...)
DJANGO_ADMINS_EMAILS_TO=

# TLS-Aktivierung (Sender E-Mail Server: True/False)
DJANGO_EMAIL_USE_TLS=

############################################
# Frontend-spezifische Konfiguration 
# (siehe .env.example in frontend repo)
############################################

# API-Endpunkt des Backends 
# (http://your-domain/api)
NEXT_PUBLIC_API_BACKEND=

# WebSocket-Endpunkt 
# (wss://your-domain/ws/sensors/)
NEXT_PUBLIC_API_WEBSOCKET_ENDPOINT=

# Analytics-Script-URL 
# (https://plausible.your-domain/js/script.js)
NEXT_PUBLIC_PLAUSIBLE_SRC=

# Analytics-Domain (your-domain)
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=

# Kontakt-E-Mail-Adresse
NEXT_PUBLIC_EMAIL_ADDRESS_CONTACT=
```


## 3.2  Konfiguration von sensitiven Daten

Secrets / Sensitive Daten für APIs werden getrennt von der Anwendung und oben beschriebenen `.env`-Datei verwaltet. 

Für Details zu deren Einrichtung verweisen wir auf Abschnitt "2.2.4 Secrets anlegen".

## 3.3 Anpassungen / Konfiguration der Anwendung

Das System wird beim initialen Start mit einer Standardkonfiguration geladen. Hierbei werden zahlreiche Einstellungen / Anwendungskonfiguration in das System importiert. Diese initiale Konfiguration ist in Dateien unter `config/init` definiert.

Folgende Konfigurationsdaten werden mitgeliefert. 


| Datei                                 | Zweck                                                       |
| ------------------------------------- | ----------------------------------------------------------- |
| `frontend_sidebar_config.json`        | Definition von Kartenlayern, Kategorien und Datenendpunkten |
| `import_model_field_config.yaml`      | Sichtbarkeit und Benennung von  Objekten in der Karte (Tabelle beim Klicken)                      |
| `datasources_config.yaml`             | Definition von Datenquellen und der entpsrechenden Resourcen                            |
| `import_data_pipeline_schedules.yaml` | Definition von Cronjobs / zeitgesteuerte Datenimporte                     |
| `sensor_types.yaml`                   | Definition von Sensortypen für MQTT                                 |

Die Konfigurationsdaten können jederzeit abgeändert und erneut in das System importiert werden (als Alternative zur Konfiguration über die Admin-Oberfläche oder bei vielen Änderungen). Details zum Import der ensprechenden Konfigdateien wird in Abschnitt "4.2 Änderungen der initialen Anwendungsdaten" beschrieben.

*Hinweis:* Es empfiehlt sich Änderungen in der Admin-Oberfläche auch stets in diesen Dateien zu nachzupflegen und versionieren, um reproduzierbare Systemstände zu gewährleisten.

## 3.4 Lokale Anwendungsdaten

Ein Großteil der Daten wird über externe Servies bezogen. Für solche Datenquellen, für kein Endpunkt zur Verfügung steht, kann der Import über eine lokale Datei erfolgen. 

Hierfür steht der Ordner `/appdata/init` zur Verfügung. Die zu importierende Dateien in dem korrekten Format der zugehörigen Datenpipeline in den oben gennatne Ordner ablegen und in dem Frontend oder der Kofiguratiosndatei (neuer Import notwendig) unter local_path diese entsprechend angeben und url leer setzen.

Beispielsweise für Wifi-Daten (datasources_config.yaml):
```
wifi_myspot_empera_pipeline:
  description: "WIFI local Pipeline"
  endpoints:
    - filename: 'wifi_myspot.xlsx'
      db_model_class: WLANHotspot
      data_source: "MySpot"
      local_path: "file://wifi_myspot.xlsx"
      url: 
```
*Hinweis*: Nach den Änderungen über die Konfigurationsdatei ist ein erneuter Import erforderlich.


## 3.5 Konfiguration des Backend-Systems (Django)

Das Backend basiert auf einem zentralen Django-Settings-Modul. Dieses steuert alle sicherheitsrelevanten und infrastrukturellen Parameter der Anwendung.

### 3.5.1 Grundprinzip

Die Django-Konfiguration folgt dem Prinzip: Konfiguration über Umgebungsvariablen – keine festen Werte im Code. Dadurch können folgende Aspekte je nach Umgebung angepasst werden:
- Debug-Modus  
- Host-Validierung  
- CORS- und CSRF-Einstellungen  
- Cookie-Domains  
- Scheduler-Aktivierung  
- E-Mail-Backend  
- Sicherheitsheader  

### 3.5.2 Sicherheitsrelevante Einstellungen

In produktiven Umgebungen sind insbesondere folgende Aspekte zu prüfen:

- `DEBUG = False`  
- Korrekte Definition von `ALLOWED_HOSTS`  
- Aktivierung sicherer Cookie-Flags  
- HTTPS-Erzwingung  
- Korrekte CSRF- und CORS-Konfiguration  

Eine fehlerhafte Konfiguration kann zu erheblichen Sicherheitsrisiken führen.

### 3.5.3 Erweiterte Anpassungen

Neben den über Umgebungsvariablen gesetzten Parametern können zusätzliche Einstellungen im Django-Settings-Modul vorgenommen werden, z.B.:

- Logging-Konfiguration  
- Caching-Strategien  
- Middleware-Erweiterungen  
- Datenbankoptimierungen  
- Performance-Parameter  

*Empfehlung*: Umgebungsspezifische Werte stets über Umgebungsvariablen steuern und das Settings-Modul möglichst generisch halten. Bei Weiterentwicklungen sollten neue konfigurierbare Parameter konsequent als Umgebungsvariablen modelliert werden.

Weiterführende Informationen zu den Django-Settings:

- [Django Settings Overview](https://docs.djangoproject.com/en/5.1/topics/settings/)  
- [Vollständige Referenz aller Settings](https://docs.djangoproject.com/en/5.1/ref/settings/)
- [Deployment-Checkliste](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
