# LautrerWissen — Backend & Data Ingestion Platform

This repository contains the **backend**, **data ingestion components**, and **containerized infrastructure** for the **LautrerWissen** smart-city data platform.

The system acquires, processes, stores, and visualizes smart city data and sensor data form various data sources (e.g., geospatial data from OSM, open data portals, wikipedia, event calendars, LoRaWAN etc.), providing a unified data backend and monitoring infrastructure.

The solution is build on the following tech stack:

![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-316192?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/-Redis-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)
![FluentBit](https://img.shields.io/badge/-Fluent--Bit-49A1E1?logo=fluentbit&logoColor=white)
![Plausible](https://img.shields.io/badge/-Plausible-5850EC?logo=plausibleanalytics&logoColor=white)
![MQTT](https://img.shields.io/badge/-MQTT-660066?logo=eclipse-mosquitto&logoColor=white)

<br>

# System Overview

The system uses a **microservice & event-driven architecture**, orchestrated via Docker Compose. Each containerized service has a single, well-defined responsibility. Together, they form a modular and scalable platform for real-time and batch data ingestion, processing, and visualization.

| Service | Role | Description |
|--------|-------------|-------------|
| **Backend (Django)** | Data Import and Management| REST API, admin UI, management for pipelines, frontend, data, users, monitoring |
| **Frontend** | User-Frontend | Public web interface (separate repo, link below) |
| **PostgreSQL** | Main database | Persistent storage for data, config & pipelines |
| **Redis** | Real-time sensor buffer | Real-time cache for sensor values |
| **MQTT Sensor Ingester** | Capture, Transform, store  MQTT events|  Streams MQTT messages → Redis (live data) |
| **MQTT Fieldstrength Ingester** | Capture, Transform, store MQTT events| Streams MQTT → PostgreSQL (signal diagnostics) |
| **Plausible Analytics** | Analytics (GDPR-friendly) | Lightweight usage & performance analytics |
| **Fluent-Bit** | Log aggregation | Logs ingestion and forwarding |
| **Health-monitoring service** | Custom Uptime & anomaly detection | Checks component health, log anomalies |

The overall system components work together by running the following workflow:

* Data Pipelines: The backend runs scheduled ETL (Extract, Transform, Load) pipelines to import data from APIs, open data portals etc.
* Persistent Storage: Data and configurations are stored in PostgreSQL.
* API Exposure: The Django backend exposes REST APIs and a management interface.
* Visualization: The frontend fetches API data to visualize it on dashboards and interactive maps.
* Monitoring & Observability: Plausible, Fluent-Bit, and the Health Monitor provide metrics, logs, and health checks.
* Real-time Data: MQTT ingesters consume live sensor data streams and update Redis for web clients.
* Client Updates: WebSocket connections push Redis-cached live data to connected users in real time.

<br>

# Component Details

The following sections describe the core backend and ingestion components. For standard services (PostgreSQL, Redis, Fluent-Bit, etc.), refer to their official documentation or configuration files in this project.

## Backend Component (Django)

The Django backend is the central service that coordinates data ingestion, management, and configuration of presentation and performs the following tasks:
* Runs data import pipelines (ETL workflows) through the pipeline_manager app. These pipelines connect to various data sources (APIs, CSVs, or open data endpoints), transform the data, and store it in PostgreSQL.
* Provides a RESTful API that exposes all imported data, configurations, and status endpoints.
* Runs scheduled import tasks (cron jobs or Celery beat workers) to refresh data periodically.
* Provides a Django Admin interface for managing users, pipelines, and configurations.
* Exposes a WebSocket endpoint to broadcast live sensor data from Redis to connected clients.
* Forwards real-time Redis messages to clients via consumer processes for real-time map and chart updates.

### Architecture

The backend is implemented in the framework Django. The backend is structured in a modular manner via the following Djnago apps: 

| Django App | Responsibility |
|-----------|--------|
| `webapp` | Core backend logic, routing, settings |
| `lautrer_wissen` | Smart-city specific models, APIs & ingestion logic |
| `frontend_config` | Configurable map & UI settings (layers, groups, names) |
| `pipeline_manager` | Config & execution of import pipelines |
| `monitoring` | Live system inspector, health & logs view |

### RESTful API-Endpoint

Data of the application (imported data and config data) is exposed via a REST endpoint under `/api/`. 

Geo-referenced data for the map-layers is served as GeoJSON for each model named 'modelname' under `/api/geo/modelname` e.g. "geo/osmleisureplayground"

## MQTT Ingestion Services

The MQTT ingesters are standalone microservices written in Python, optimized for handling real-time IoT data streams. The components run as consumer services, connect to the MQTT broker on specifc topics. Topics which are subscribed can be configurable via the environmental variable `MQTT_TOPIC_SELECTOR`. 

The component *MQTT Sensor Ingeste* performs the following tasks:
- Parses incoming messages (JSON / LoRaWAN payload)
- Writes real-time data to **Redis** for quick access and WebSocket streaming

The component *MQTT Fieldstrength Ingeste* performs the following tasks:
- Parses incoming messages (JSON / LoRaWAN payload)
- Writes processed data to **PostgreSQL** for persistence and analytics


## Supporting Services

All services are defined in the main `docker-compose.yaml`. Supporting components include:
* PostgreSQL: Database for all persistent data
* Redis: Fast in-memory storage for real-time caching
* Plausible Analytics: Self-hosted analytics dashboard
* Fluent-Bit: Centralized log collection and forwarding
* Health Monitor: Sidecar app for system health and uptime checks

<br>

# Getting Started

## Prerequisites

- Docker & Docker Compose installed
- Unix-based environment recommended (Linux/Mac)
- 4 GB RAM minimum for local setup

### Start all services

To build and start all containers:

```bash
docker-compose -f compose.yaml up --build
```


To run in detached mode:

```bash
docker-compose -f compose.yaml up -d
```

<br>


# Project Structure

The project layout is organized in a modular manner, ensuring clear separation of backend, ingestion, and monitoring logic:

```
lauter_wissen
│
├── ingestor/                        # data ingestor code
│   ├── apis                         # impl. of data connectors for APIs
│   ├── datapipe                     # impl. of data processing pipelines
│   └── ...
│
├── webapp/                          # Django 'backend' webapp
│   ├── frontend_config              # specific Djnago apps
│   ├── lautrer_wissen
│   ├── monitoring
│   └── ...
│
├── monitoring/                      # Sidecar app for monitoring
│   ├── analyzer/
│   └── ...
│
├── docker/                          # Application specific Docker containers
│   ├── webapp.Dockerfile
│   ├── ingestor_streaming.Dockerfile
│   └── monitoring.Dockerfile
│
├── config/                          # Configurationd data
│   ├── init/                        # Django DB seed/init configs (e.g. sidebar, data pipelines etc.)
│   └── components/                  # component configs (fluentbit, monitoring...)
│
├── appdata/                         # Specific application data
    └── initial/                     # Seed/init data (e.g. for data without an API-Endpoint),

```


# License and Contact

## Open-Source Licenses

This project uses open-source components, including:

- Django & Django REST Framework — BSD-3
- Django Channels & Daphne — BSD-3
- Django-APScheduler — BSD-3
- PostgreSQL — PostgreSQL License
- Redis — BSD-3
- psycopg — LGPL-3 (server-side use, compliant)
- Pandas / GeoPandas / Shapely — BSD-3
- OWSLib — GPL-3 (server-side use only, no linking in distributed binaries)
- Docker & Docker Compose — Apache-2.0
- Plausible — AGPL-3 (self-hosted, unmodified)

For a complete list of third-party licenses, see the NOTICE file and requirements.txt.

## Contact
E-Mail: info[at]vision-impulse.com

## Legal
&copy; 2025 Vision Impulse GmbH • License: [AGPLv3](LICENSE)  
Implemented by [Vision Impulse GmbH](https://www.vision-impulse.com)


