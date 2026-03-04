# 4 Update- und Wartungskonzept

Dieses Kapitel beschreibt empfohlene Vorgehensweisen für Updates, Wartung, Monitoring und den stabilen Betrieb der Anwendung. 

## 4.1 Regelmäßige Updates des Systems

Regelmäßige Updates sind essenziell für:

- Sicherheit (Schließen von Sicherheitslücken)
- Stabilität und Performance
- Kompatibilität mit externen Diensten
- Langfristige Wartbarkeit

### 4.1.1 Aktualisierung der Softwarekomponenten

Folgende Bestandteile sollten regelmäßig überprüft und aktualisiert werden:

#### 1. Docker Basis-Images

- Aktualisierung der Images in `compose.yaml` (z. B. Datenbank-, Cache- oder Proxy-Images)
- Aktualisierung der Basis-Images in projektspezifischen Dockerfiles (Backend, Frontend etc.)

Beispiel:

```dockerfile
FROM python:3.x-slim
FROM node:xx-alpine
```

#### 2. Abhängigkeiten innerhalb der Komponenten

- Python-Abhängigkeiten (`requirements.txt`)
- Node-Abhängigkeiten (`package.json`)
- Systempakete innerhalb der Container

Nach Aktualisierung der Abhängigkeiten sollte ein vollständiger Rebuild erfolgen.

#### 3. Änderungen am Quellcode

- Einspielen neuer Releases
- Sicherheitsrelevante Fixes
- Funktionale Erweiterungen


### 4.1.2 Durchführung eines Updates (Produktionssystem)

#### 1. Container kontrolliert stoppen

```bash
docker compose -f compose.yaml -f docker/compose/compose.prod.yaml down
```

#### 2. Images neu bauen und Container starten

```bash
docker compose -f compose.yaml -f docker/compose/compose.prod.yaml \
  --env-file .env.prod up -d --build
```

Der Parameter `--build` stellt sicher, dass neue Images erzeugt werden.

Falls Docker Layer cached, kann ein vollständiger Neuaufbau erzwungen werden:

```bash
docker compose build --no-cache
```

#### Wichtige Hinweise

- Updates zunächst in einer Staging-Umgebung testen
- Vor größeren Versionssprüngen (insbesondere Datenbank) ein Backup erstellen
- Changelogs der verwendeten Images prüfen


### 4.1.3 Update des Host-Systems

Neben der Anwendung selbst muss auch das Host-System regelmäßig gewartet werden:

- Sicherheitsupdates des Betriebssystems durchführen  
  ```bash
  apt update && apt upgrade
  ```
- Docker Engine und Docker Compose aktuell halten
- Firewall- und Netzwerkeinstellungen überprüfen
- TLS-Zertifikate regelmäßig erneuern (z.B. automatisiert über Let's Encrypt)


### 4.1.4 Überprüfung von Benutzer- und Zugriffsdaten

Im Rahmen regelmäßiger Wartung sollten außerdem geprüft werden:

- Nicht mehr benötigte Benutzerkonten deaktivieren oder entfernen
- Rollen- und Rechtevergabe kontrollieren
- Secrets regelmäßig rotieren
- API-Zugriffe validieren


# 4.2 Änderungen der Anwendungsdaten

Das LautrerWissen verwendet initiale Konfigurationsdateien (siehe Kapitel 3.2) und statische Daten (ohne API) für den initialen Import von: 
- Datenpipelines
- Cron-Jobs
- Kartenlayer
- Sichtbarkeitsregeln
- Weitere initiale Konfigurationsdaten
- statischer Datenimport

Diese Konfigurationsdateien befinden sich im Verzeichnis:

```
config/init
```

Diese Daten können jederzeit geändert und erneut in das System importiert werden. 

*Hinweis*: Der Container mit dem `core-backend` muss dafür laufen. 

Es stehen folgende Befehle zur Verfügung:


## 4.2.1 Reimport der Frontend-Konfiguration

### Kartenlayer / Sidebar

```bash
docker exec -it core-backend \
  python3 /lautrer_wissen_backend/webapp/manage.py \
  import_maplayer_config --force
```

Konfigurationsdatei:

```
config/init/frontend_sidebar_config.json
```

---

### Sichtbare Modellattribute

```bash
docker exec -it core-backend \
  python3 /lautrer_wissen_backend/webapp/manage.py \
  import_model_field_config --force
```

Konfigurationsdatei:

```
config/init/models_field_config.yaml
```

---

## 4.2.2 Reimport der Datenpipelines

### Datenquellen und Ressourcen

```bash
docker exec -it core-backend \
  python3 /lautrer_wissen_backend/webapp/manage.py \
  import_data_pipelines --force
```

Konfigurationsdatei:

```
config/init/datasources_config.yaml
```

---

### Zeitgesteuerte Pipeline-Ausführung (CronJobs)

```bash
docker exec -it core-backend \
  python3 /lautrer_wissen_backend/webapp/manage.py \
  import_data_pipeline_schedules --force
```

Konfigurationsdatei:

```
config/init/datasources_schedules_config.yaml
```

---

## 4.2.3 Reimport von statischen Daten

Neben Konfigurationsdaten können auch statische Daten ohne einen öffentlichen API Zugang importiert werden. 

Die entsprechenden Dateien für den Import befinden sich in dem Ordner `./app_data/init/`.

Diese können jederzeit geändert und erneut in das System importiert werden über folgende Befehle:

### Reimport der Daten für Dashboards (statisch):
```bash
docker exec -it core-backend python3 /lautrer_wissen_backend/webapp/manage.py import_dashboards –force
```

--- 

### Reimport der Daten zur Bundestagswahl (statisch):
```bash
docker exec -it core-backend python3 /lautrer_wissen_backend/webapp/manage.py import_elections --force
```

--- 

### Reimport der Daten zur Feldmessung aus einem externen DB-Dump:
```bash
docker exec -it core-backend python3 /lautrer_wissen_backend/webapp/manage.py import_fieldtests --force
```


# 4.3 Wartung, Monitoring und Betrieb

## 4.3.1 Überwachung der Docker-Komponenten

### Laufende Container anzeigen

```bash
docker ps
```

### Logs prüfen

```bash
docker logs <container-name>
```

---

## 4.3.2 System-Monitoring innerhalb der Anwendung

Ein separater Monitoring-Container überprüft regelmäßig die Erreichbarkeit und den Status aller Systemkomponenten.

Die aktuellen Zustände können in der Administrationsoberfläche des Backends unter:

```
System-Monitoring → Docker Containers
```

eingesehen werden.

---

## 4.3.3 Datenbank-Backup

### Manuelles Backup erstellen

```bash
docker exec -t core-database \
  pg_dump -U <POSTGRES_USER> <POSTGRES_DB> > backup.sql
```

### Wiederherstellung

```bash
docker exec -i core-database \
  psql -U <POSTGRES_USER> <POSTGRES_DB> < backup.sql
```

Ein automatisiertes Backup (z.B. via Cronjob) wird dringend empfohlen. Ebenfalls:
- Backups regelmäßig durchführen
- Versioniert speichern
- Offsite-Backup vorhalten
- Wiederherstellung regelmäßig testen

---

## 4.3.4 Neustart einzelner Services

### Einzelnen Service neu starten

```bash
docker compose restart core-backend --env-file .env.prod
```

### Gesamtes System neu starten

```bash
docker compose -f compose.yaml -f docker/compose/compose.prod.yaml \
  restart --env-file .env.prod
```
