# Nutzer-Handbuch – LautrerWissen

## 1 Zweck des Dokuments

Dieses Dokument beschreibt die Administration und Konfiguration des LauterWissens über die bereitgestellte Administrationsoberfläche (Backend). Es richtet sich an Personen, die vorhandene Datenpipelines, statische Daten sowie deren Darstellung in der Anwendung konfigurieren und pflegen.
Technische Details zur Systemarchitektur, Installation und Wartung sind nicht Bestandteil dieses Dokuments, sondern werden im gesonderten Administrationshandbuch beschrieben.

Ziel ist es, den Nutzenden eine praxisorientierte Anleitung zur Anpassung der Anwendungsdaten zu geben – ohne tiefgehende technische Kenntnisse zu 
erfordern.

## 1.1 Zielgruppe

Das Handbuch richtet sich primär an:
*	Fachadministratoren oder Redakteuren, die bestehende Datenquellen, Importprozesse und Darstellungen konfigurieren
*	Projektverantwortliche, die die Datenpflege und -darstellung im System betreuen
*	Systemadministratoren, die ergänzend für Rechteverwaltung und Benutzerkonfiguration zuständig sind

Der technische Aufbau, die Installation und die Systemwartung sind nicht Teil dieses Dokuments und ausschließlich für Systemadministratoren im Rahmen des separaten Admin-Handbuchs relevant.

## 1.2 Überblick über das System
Über das Backend des LauterWissens wird eine zentrale Administrationsoberfläche bereitgestellt, in der die grundlegende Konfiguration von Anwendungsdaten vorgenommen wird. Folgende zentrale Bereiche können dort konfiguriert werden:
*	Datenimport-Pipelines (Schnittstellen, Verarbeitungsschritte, Zeitsteuerung über Cron-Jobs)
*	Statische Daten (manuell gepflegte oder einmalig importierte Datensätze)
*	Darstellung der Daten in der Karte des LauterWissens (Layer, Symbole, Filter, Pop-ups)
*	Benutzer-, Gruppen- und Berechtigungsverwaltung

Darüber hinaus bietet das System:
*	Ein Dashboard zur Systemüberwachung, in dem der Status der Backend-Komponenten (z. B. Docker-Container, Hintergrundprozesse) angezeigt wird
*	Zugriff auf Logdateien zur Fehleranalyse und Systemdiagnose
*	(Optional) Monitoring- und Benachrichtigungsfunktionen bei fehlerhaften Imports

## 1.3 Voraussetzungen

Für die Nutzung der Administrationsoberfläche gelten folgende Voraussetzungen:
*	Ein Benutzerkonto mit ausreichenden Berechtigungen (z. B. Rolle „Administrator“ oder „Datenmanager“)
*	Zugang zur Administrationsoberfläche des LauterWissens über den Link `https://app-domain-name/admin`
 
## 1.4 Aufbau des Handbuchs

Die weiteren Kapitel dieses Dokuments sind thematisch strukturiert und behandeln unter anderem die Konfiguration, Arbeitsschritte und das Management der Daten: 

* [`Management der Datenquellen und des Datenimports`](./data_management.md) 
* [`Konfiguration des Frontends`](./frontend_configuration.md) 
* [`Management von Nutzern, Gruppen und Berechtigungen`](./user_management.md) 

