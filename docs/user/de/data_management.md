# 2 Konfiguration der Datenimport-Pipelines
## 2.1 Zweck und Funktionsweise der Datenpipelines

Datenpipelines bilden das Rückgrat der automatisierten Datenverarbeitung im LauterWissen. Sie dienen dazu, externe Datenquellen (Schnittstellen, Dateien, Feeds oder APIs) automatisiert abzurufen, die Daten zu verarbeiten, zu transformieren und in die Datenbank des Systems zu importieren.
Die grundlegende Aufgabenfolge einer Pipeline umfasst typischerweise:
*	Abruf der Daten – über eine definierte Schnittstelle (z. B. REST-API, XML-Endpunkt, CSV-Datei, GeoJSON)
*	Transformation und Filterung – Anpassung der Datenstruktur, Bereinigung fehlerhafter Werte, Filterung nach relevanten Kriterien (z.B. nach Geo-Koordinaten innerhalb des Stadtgebiets)
*	Validierung – Prüfung auf Plausibilität, Vollständigkeit und Datenkonsistenz
*	Import in das Datenmodell – Speicherung der transformierten Datensätze in einer oder mehreren Datenbanktabellen, die im Backend unter der Kategorie „Modelle“ verwaltet werden

Jede Pipeline ist individuell implementiert und berücksichtigt die spezifischen Anforderungen der jeweiligen Datenquelle.
Änderungen an der Struktur, dem Format oder der Logik der Quellschnittstelle erfordern in der Regel Anpassungen am Softwaremodul der Pipeline selbst – diese können nicht über das Backend vorgenommen werden, sondern müssen im Quellcode erfolgen.

## 2.2 Beziehung zwischen Pipelines und Modellen
Ein wesentliches Konzept im LauterWissen ist die Trennung zwischen Pipelines (Verarbeitung) und Modellen (Datenstruktur).
*	Modelle repräsentieren die Datenobjekte, die im System gespeichert werden (z.B. Veranstaltungen, Orte, Wikipedia-Einträge in der Tabelle).
*	Pipelines definieren den Weg, wie Daten in diese Modelle gelangen.

Eine einzelne Pipeline kann mehrere Modelle mit Daten versorgen.

Beispiel: Die Pipeline Wikipedia ruft mehrere Wikipedia-Seiten nacheinander ab. Der Workflow (Abruf, Transformation, Import) ist grundsätzlich identisch, die jeweiligen Transformationen (z. B. welche Textabschnitte extrahiert werden) unterscheiden sich jedoch pro Ressource und müssen individuell in der Software definiert werden.

Beispiel: Umgekehrt kann auch ein Modell von mehreren Pipelines befüllt werden (z.B. wenn verschiedene Datenquellen dieselbe Datentabelle erweitern oder aktualisieren, dies ist beispielsweise bei Wifi-Hotspots der Fall).

## 2.3 Zugriff auf Pipelines und Modelle

In der Administrationsoberfläche finden Sie die entsprechenden Bereiche:
*	Pipelines:  Menüpunkt → „Pipelines“ → Übersicht aller implementierten Datenimport-Pipelines
*	Modelle:    Menüpunkt → „Daten-Modelle“ → Anzeige und Verwaltung der Datensätze, die aus den Pipelines generiert wurden

Diese Trennung unterstützt sowohl die Wartung als auch die Nachvollziehbarkeit von Datenquellen und -flüssen.

## 2.4 Übersicht der vorhandenen Pipelines

Unter dem Menüpunkt „Pipelines“ werden alle aktuell verfügbaren Datenpipelines aufgelistet. Für jede Pipeline werden in der Übersicht typischerweise folgende Informationen angezeigt:

Markdown
| Nr. | Name | Datentyp | Beschreibung |
| :-- | :--- | :-- | :----------- |
| 1 | `Ratsveranstaltungen (RSS) Import` | Veranstaltungen | Diese Pipeline importiert Veranstaltungen aus dem Ratsinformationssystem (RIS). Aktuell existiert keine Schnittstelle, daher wird der RSS-Feed verwendet |
| 2 | `Veranstaltungen (MIADI)` | Veranstaltungen | Veranstaltungen (MIADI)	Diese Pipeline importiert Veranstaltungen aus dem Veranstaltungskalender der Stadt Kaiserslautern. Es wir die MIADI-XML Schnittstelle verwendet. |
| 3 | `Veranstaltungen (Was Geht App?)` | Veranstaltungen | Diese Pipeline importiert Veranstaltungen aus dem externen Veranstaltungskalender Plattform „Was geht App?“. Es wird ein HTTP-Endpunkt mit JSON-Format angesprochen. |
| 4 | `TTN Gateway Import` | Geodaten | Diese Pipeline importiert Daten für das Modell TTN-Gateway. Es wird eine öffentlicher http-Endpunkt mit JSON-Format angesprochen. |
| 5 | `Wifi Import` | Geodaten | Diese Pipeline importiert Daten für das Modell Wifi-Hotspot der Datenquelle Freifunk. Es wird ein öffentlicher HTTP-Endpunkt mit JSON-Format angesprochen. |
| 6 | `E-Ladestationen Import` | Geodaten | Diese Pipeline importiert E-Ladestationen über die bereitgestellte CSV-Datei auf der Webseite der Bundesnetzagentur. Quelle: https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/Ladesaeulenkarte/start.html (Unter Downloads und Formulare -> Liste der Ladesäulen als CSV) |
| 7 | `Geodaten Import KL` | Geodaten | Diese Pipeline importiert GeoDaten, die als geojson-Datei vorliegen. Die Dateien werden derzeit über das OpenData-Portal der Stadtverwaltung Kaiserslautern heruntergeladen. |
| 8 | `Geodaten WFS Import` | Geodaten | Diese Pipeline importiert GeoDaten, die über eine Web Feature Service-Schnittstelle (WFS) vorliegen. Die Dateien werden derzeit über das Geoportal der Stadtverwaltung Kaiserslautern bezogen. |
| 9 | `Sensor (MQTT) Import` | Geodaten | Diese Pipeline importiert die Standorte der Sensoren (Es werden keine Sensor-Werte importiert). Die Pipeline verbindet sich auf den MQTT-Broker und liest alle Sensoren aus, die zu dem in der Installation gesetzten regulären Ausdruck in MQTT_TOPIC_SELECTION matched. (aktuell: ^geo.*sensor) |
| 10 | `Open Street Map Import` | Geodaten | Diese Pipeline importiert die Inhalte von OSM. Die Pipeline kann für mehrere unterschiedliche OSM-Objekte ausgeführt werden. Unter dem Attribut Tags: kann die Selektion der OSM-Objekte angegeben werden. Zusätzliche spezifische Einschränkungen bedürfen softwareseitig einer individuellen Anpassung. |
| 11 | `Rettungspunkte Import` | Geodaten | Diese Pipeline importiert Rettungspunkte über die bereitgestellte Shape-Datei im Zip Archiv auf der Webseite der KWF Online. Quelle: https://kwf2020.kwf-online.de/rettungspunkte-download-ja/ (Unter Downloads -> Gesamtdatensatz - Shape) |
| 12 | `VRN Haltestellen Import` | Geodaten | Diese Pipeline importiert Bushaltestellen über das Open Data Portal der VRN. Die Daten stehen als Zip-Datei zur Verfügung und werden (in der Regel unter gleicher URL) aktualisiert. |
| 13 | `Wikipedia Import` | Geodaten | Diese Pipeline importiert die Inhalte von einzelnen Wikipedia Seiten. Die Pipeline kann für mehrere Wikipedia Seiten ausgeführt werden. Es können grundlegende Informationen für jede zu verarbeitende Wikipedia-Seite konfiguriert werden (Name der Seite, Angabe der Nummer der Tabelle auf der Seite, einzusetzende Klasse der Tabellenextraktion und Datenhaltung). |


## 2.5 Konfiguration einer Datenpipeline
Jede Pipeline ist softwareseitig in mehrere Verarbeitungsschritte (Module) unterteilt, die zusammen den ETL-Prozess (Extract, Transform, Load) bilden. Im Backend können Sie verschiedene konfigurierbare Eigenschaften einer Pipeline anpassen, ohne den Code zu ändern.
Unter dem Reiter „Ressourcen“ können einzelne Datenquellen (z. B. API-Endpunkte, Dateipfade, URLs) eingesehen und bearbeitet werden. Hier können Sie:
*	die URL oder den Pfad einer Ressource ändern,
*	eine Ressource aktivieren oder deaktivieren (z.B. bei temporär nicht verfügbaren Quellen),
*	optionale Parameter wie Filter definieren.

Beispiel: Eine MIADI-Pipeline hat genau eine Ressource (z.B. einen XML-Endpunkt).

Beispiel: Die Wikipedia-Pipeline dagegen kann mehrere Ressourcen (mehrere Wikipedia-Seiten) enthalten, die nacheinander verarbeitet werden. Sofern eine Seite nicht erreichbar ist oder eine strukturelle Änderung unterworfen ist, kann diese deaktiviert werden und die Pipeline für die verbleibenden Ressourcen (Wikipedia Seiten) ausgeführt werden.

## 2.6 Ausführen von Datenpipelines
Über den Button „Run“ in der Pipeline-Übersicht kann eine Datenpipeline manuell gestartet werden. Dies ist sinnvoll, wenn:
*	sich Datenquellen geändert haben und ein sofortiger Reimport notwendig ist,
*	nach einer Konfigurationsänderung die aktuelle Datenbasis aktualisiert werden soll,
*	eine Pipeline bei einem automatischen Lauf fehlerhaft war und erneut ausgeführt werden soll.

Während der Ausführung werden der Fortschritt und der Status (laufend, erfolgreich, fehlerhaft) angezeigt.
Pipelines können automatisiert in regelmäßigen Intervallen gestartet werden.

Diese Zeitsteuerung erfolgt über Cron-Jobs, die unter dem Reiter „Pipeline-CronJobs“ konfiguriert werden können.
Jede Pipeline kann einen individuellen Cron-Ausdruck erhalten, z. B.:
* 0 4 * * * 	→ täglich um 4:00 Uhr
* 30 2 * * 1 	→ montags um 2:30 Uhr

Empfehlung:
*	Vermeiden Sie, dass alle Pipelines gleichzeitig starten.
*	Berücksichtigen Sie die Laufzeit einzelner Pipelines (kurze Importe: Sekunden; umfangreiche wie Wikipedia: mehrere Minuten).

## 2.7 Monitoring, Fehleranalyse und Best Practices
Unter dem Reiter „Pipeline-Runs“ werden alle ausgeführten Pipeline-Läufe (manuell und automatisch) protokolliert. Die Tabelle zeigt u.a. den Status, die Dauer, Name der Pipeline und Startzeit. Fehlerhafte Läufe können im Log detailliert untersucht werden.

### 2.7.1 Fehleranalysen
Typische Ursachen für Fehler während der Ausführung:
*	API-Endpunkt ist nicht erreichbar
*	Formatänderungen in der Quelle
*	Authentifizierungsfehler
*	Zeitüberschreitungen (Timeouts)

### 2.7.2 Best Practices
Bei dem Erstellen, Änderungen oder Ausführen der Datenpipelines empfehlen wir die folgenden Best Practices und Hinweise:
*	Testen Sie Änderungen an Ressourcen zunächst manuell, bevor Sie Cron-Jobs aktivieren.
*	Führen Sie keine parallelen Läufe derselben Pipeline aus, um Dateninkonsistenzen zu vermeiden.
*	Nutzen Sie das Monitoring regelmäßig, um fehlerhafte Datenquellen frühzeitig zu erkennen.
*	Dokumentieren Sie Änderungen an Endpunkten oder Ressourcen (z. B. in einem Änderungsprotokoll). Wir empfehlen Ihnen die Änderungen in der Konfigurations-Datei `/config/init/datasources_config.yaml` bzw. einer entsprechenden Kopie nachzupflegen und zu versionieren. Im Falle einer korrupten Datenbank, können die vorgenommenen Änderungen somit jederzeit widerhergestellt oder neu importiert werden.



