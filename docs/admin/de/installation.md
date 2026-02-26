# 2 Infrastruktur, Installation und Deployment

Dieser Abschnitt beschreibt die Infrastruktur-Anforderungen sowie die Installation der Anwendung für Entwicklungs- und Produktionsumgebungen.

# 2.1 Infrastruktur

Für die Installation und den Betrieb wird eine Instanz mit folgender Mindestspezifikation benötigt:

* **Zielplattform:** Linux-Server oder Cloud-Instanz mit mindestens **8 GB RAM** und **4 CPU-Kernen**
* **Betriebssystem:** Debian oder äquivalent (z. B. Ubuntu Server LTS)
* **Software:** Installation von **Docker** (inkl. Docker Compose Plugin).

Alle weiteren Software-Komponenten (Datenbank, Redis, Backend, Frontend etc.) sind vollständig in Docker-Containern gekapselt.

## Empfohlene Zusatzanforderungen (Produktion)

* Öffentliche IP-Adresse oder Domain
* Firewall-Konfiguration (nur notwendige Ports freigeben)
* TLS-Zertifikate (z. B. via Let’s Encrypt)
* Reverse Proxy (siehe Abschnitt 2.3)


# 2.2 Installation

## 2.2.1 Installation der Docker Runtime

Falls Docker noch nicht installiert ist, der offiziellen [Installationsanleitung](https://docs.docker.com/engine/install) der Docker Engine und Docker compose folgen. Anschließend docker starten:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

Optional: aktuellen Benutzer zur Docker-Gruppe hinzufügen:

```bash
sudo usermod -aG docker $USER
```

Anschließend neu einloggen.


## 2.2.2 Projektordner erstellen und Repositories klonen

```bash
mkdir lautrerwissen
cd lautrerwissen

git clone https://github.com/vision-impulse/LautrerWissen-Frontend
git clone https://github.com/vision-impulse/LautrerWissen-Backend
```

Die Docker-Compose-Dateien befinden sich im Backend-Repository.


## 2.2.3 Umgebungsvariablen konfigurieren

### Für die Produktionsumgebung

```bash
cp .env.example .env.prod
vi .env.prod
```

Wichtig:
* `DJANGO_ENV=prod` setzen
* Alle produktionsrelevanten Variablen anpassen

Details zu einzelnen Variablen sind im Abschnitt „3. Konfiguration" beschrieben.

### Für die Entwicklungsumgebung

```bash
cp .env.example .env
vi .env
```

Wichtig:
* `DJANGO_ENV=dev` setzen


## 2.2.4 Secrets anlegen

### Für die Produktionsumgebung

Secrets werden außerhalb des Projektordners gespeichert.

```bash
sudo mkdir -p /etc/lautrerwissen/secrets
sudo chmod 700 /etc/lautrerwissen/secrets
sudo chown root:root /etc/lautrerwissen/secrets
```

Beispiel: Datenbank-Secrets anlegen

```bash
cp ./secrets/db_secrets.example /etc/lautrerwissen/secrets/db_secrets
sudo vi /etc/lautrerwissen/secrets/db_secrets
sudo chmod 600 /etc/lautrerwissen/secrets/db_secrets
sudo chown root:root /etc/lautrerwissen/secrets/db_secrets
```

Analog für weitere Secret-Dateien (z.B. `mqtt_secrets`, `django_secrets` etc.).

### Für die Entwicklungsumgebung

```bash
cp ./secrets/db_secrets.example ./secrets/db_secrets
vi ./secrets/db_secrets
```

In der Entwicklungsumgebung können Secrets lokal im Projektordner abgelegt werden.


## 2.2.5 Starten der Komponenten

Alle Abhängigkeiten zwischen den Containern sind im Docker-Compose definiert.

### Für die Produktionsumgebung

Start der Kernservices:

```bash
docker compose -f compose.yaml -f docker/compose/compose.prod.yaml up -d --build
```

Start von Plausible (separate Compose-Dateien):

```bash
docker compose -f compose.plausible.yaml -f docker/compose/compose.plausible.prod.yaml up -d
```

### Für die Entwicklungsumgebung

```bash
docker compose -f compose.yaml -f docker/compose/compose.dev.yaml up -d --build
```


## 2.2.6 Überprüfung der Installation

Status der Container prüfen:

```bash
docker ps
```

### Für die Produktionsumgebung

Die Container laufen intern im Docker-Netzwerk. Für die öffentliche Erreichbarkeit ist ein Reverse Proxy erforderlich (siehe Abschnitt 4.3 Deployment).

### Für die Entwicklungsumgebung

Erreichbarkeit der konfigurierten Endpunkte prüfen. 

Beispiel-Endpunkte:
* [http://localhost:3000](http://localhost:3000) für das Frontend
* [http://localhost:8002](http://localhost:8002) für das Backend



# 2.3 Deployment mit Reverse Proxy

Nach erfolgreicher Installation laufen alle Softwaremodule innerhalb des Docker-Netzwerks.
Für den Produktivbetrieb muss die Anwendung jedoch:

* über eine (Sub-)Domain erreichbar sein
* ausschließlich über HTTPS bereitgestellt werden
* hinter einem Reverse Proxy betrieben werden

Die konkrete Implementierung ist unabhängig vom Anwendungssystem. Bestehende Reverse-Proxies können erweitert oder ein neuer Proxy kann dediziert für diese Anwendung betrieben werden. Das Deployment der Anwendung ist technisch unabhängig von der gewählten Reverse-Proxy-Lösung.

Im Folgenden werden die wesentlichen Punkte beschrieben.


## 2.3.1 Grundanforderungen

* Verwendung eines Reverse Proxy (z.B. Nginx oder Traefik)
* TLS-Konfiguration (z.B. via Let’s Encrypt)
* Weiterleitung aller HTTP-Anfragen (Port 80) auf HTTPS (Port 443)
* Keine direkte Veröffentlichung der Backend- oder Datenbank-Ports

Das Backend lehnt unsichere HTTP-Anfragen ab. Eine korrekte Weitergabe des Headers `X-Forwarded-Proto` ist daher zwingend erforderlich.


## 2.3.2 Routing-Regeln

Der Reverse Proxy muss die Requests wie folgt verteilen:

* `/api/` → Backend
* `/admin/` → Backend
* `/ws/sensors/` → Backend (WebSocket)
* alle übrigen Requests (`/`) → Frontend


## 2.3.3 Exemplarische Nginx-Konfiguration

**Hinweis:** Die folgende Konfiguration dient als Beispiel! Sicherheitsmaßnahmen wie TLS-Konfiguration, HSTS, Rate Limiting oder zusätzliche Header sollten produktionsspezifisch ergänzt werden. 

**Hinweis:** Die Konfiguration geht davon aus, dass der Nginx-Server in dem gleichen Docker-Netzwerk befindet wie die Komponenten (Backend, Frontend).

```nginx
server {
    listen 80;
    server_name example.com;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Security Header (empfohlen)
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # Frontend
    location / {
        proxy_pass          http://frontend:3000;
        proxy_set_header    Host $host;
        proxy_set_header    X-Real-IP $remote_addr;
        proxy_set_header    X-Forwarded-Proto $scheme;
        proxy_set_header    X-Forwarded-Host $server_name;
        proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://backend:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass_header Set-Cookie;
        proxy_set_header Origin $http_origin;
        proxy_set_header Referer $http_referer;
    }

    # WebSocket Support
    location /ws/sensors/ {
        proxy_pass http://backend:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Statische Dateien von Django
    location /static/ {
        alias /lautrerwissen-web-static/;
    }
}
```


## 2.3.4 Bereitstellung statischer Dateien

Für optimale Performance sollten statische Inhalte (Bilder, CSS, JavaScript) direkt vom Reverse Proxy ausgeliefert werden. Dazu:
* Das Django-Static-Volume im Reverse-Proxy-Container mounten
* Im Nginx mittels `alias` bereitstellen (siehe oben)

Beispiel Docker-Mount im Proxy-Container für nginx (in der docker-compose.yaml für nginx):

``` 
    volumes:
      - lautrerwissen-web-static:/lautrerwissen-web-static:ro
```

## 2.3.5 Domain-Konfiguration

Abschließend müssen die Domain und die öffentlichen URLs in den Konfigurationsdateien gesetzt werden:

* Frontend-Umgebungsvariablen (z.B. `NEXT_PUBLIC_API_BACKEND`)
* Backend-Umgebungsvariablen (`ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, etc.)

Siehe Abschnitt 2.2 sowie Kapitel 3 Konfiguration.


## 2.3.6 Neustart der Komponenten

Nach Anpassung der Domain- oder Proxy-Konfiguration:

```bash
docker compose -f compose.yaml -f docker/compose/compose.prod.yaml up -d --build
```

Das System ist nun produktionsbereit über eine gesicherte HTTPS-Domain erreichbar.


## 2.3.7 Sicherheitshinweise für Produktion

Empfohlene zusätzliche Maßnahmen:

* Absicherung des Admin-Bereichs (IP-Whitelist oder Basic Auth zusätzlich möglich)
* Regelmäßige Erneuerung der TLS-Zertifikate
* Keine Veröffentlichung interner Docker-Ports
* Rate Limiting für `/api/`
