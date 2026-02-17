# Konfiguration von Nutzern, Gruppen und Berechtigungen

## Zweck und Überblick
Das LauterWissen-System verfügt über ein rollenbasiertes Berechtigungssystem, das sicherstellt, dass nur autorisierte Personen Zugriff auf administrative Funktionen und Daten haben. Über den Menüpunkt „Nutzerverwaltung“ (bestehend aus den Reitern Users und Groups) können Benutzerkonten, Gruppen und deren Berechtigungen verwaltet werden. Das System unterscheidet dabei zwischen:
*	Einzelnen Nutzern, die sich anmelden können,
*	Gruppen, über die Berechtigungen zentral verwaltet werden,
*	und Superusern, die uneingeschränkten Zugriff besitzen.

Die Einrichtung und Pflege von Benutzern und Gruppen sollte nur durch Personen mit administrativen Rechten erfolgen.

## Gruppenverwaltung
### Anlegen und Bearbeiten von Gruppen
Unter dem Menüpunkt „Groups“ können bestehende Gruppen angezeigt, bearbeitet oder neue Gruppen angelegt werden. Gruppen dienen als Container für Berechtigungen, die anschließend mehreren Nutzern gleichzeitig zugewiesen werden können.
Typische Gruppenbeispiele:
*	Datenredakteure – dürfen Inhalte und Datenquellen pflegen, jedoch keine Systemänderungen vornehmen
*	Fachadministratoren – dürfen Import-Pipelines, Modelle und Kartenkonfigurationen anpassen
*	Systemadministratoren – haben Vollzugriff auf alle Backend-Bereiche

Beim Anlegen einer Gruppe wird ein Gruppenname vergeben. Im Formularfeld „Permissions“ können anschließend Berechtigungen (Rechte) für diese Gruppe ausgewählt werden.

### Zuweisung von Berechtigungen
Im Feld „Permissions“ werden alle verfügbaren Rechte des Systems aufgelistet.
Diese Rechte beziehen sich in der Regel auf konkrete Modelle oder Funktionen (z.B. Add, Change, Delete, View für bestimmte Datentypen).

Empfehlung: Berechtigungen sollten grundsätzlich über Gruppen verwaltet werden, um die Administration übersichtlich und konsistent zu halten. Einzelberechtigungen für Nutzer sollten nur in Ausnahmefällen vergeben werden.

## Benutzerverwaltung
### Übersicht und Verwaltung
Unter dem Menüpunkt „Users“ können alle vorhandenen Benutzerkonten eingesehen, bearbeitet oder neue Nutzer angelegt werden. Die Benutzerliste zeigt unter anderem folgende Informationen:
*	Benutzername
*	Aktivitätsstatus
*	Zugeordnete Gruppen
*	Superuser-Status

### Anlegen neuer Nutzer
*	Öffnen Sie im Menü „Users“ die Option Add user.
*	Geben Sie im Formular folgende Informationen an:
*	Username (eindeutiger Login-Name)
*	Passwort (muss den internen Sicherheitsrichtlinien entsprechen)
*	Speichern Sie den neuen Nutzer mit Save.

Nach dem Speichern ist der Nutzer angelegt, besitzt jedoch noch keine Berechtigungen. Damit sich der Benutzer anmelden und arbeiten kann, sind folgende Schritte erforderlich:

| Schritt	| Beschreibung |
| :----  | :----------- |
| 1. Staff User aktivieren	| Setzen Sie die Checkbox „Staff User“, um den Zugriff auf die Administrationsoberfläche zu erlauben. Ohne diese Option ist kein Login im Backend möglich. |
| 2. Gruppe zuweisen | Unter dem Tab „Permissions“ muss mindestens eine Gruppe ausgewählt werden. Nur so erhält der Nutzer Sicht- und Bearbeitungsrechte. |
| 3. (Optional) Superuser aktivieren | Mit der Checkbox „Superuser Status“ erhält der Nutzer automatisch alle Berechtigungen, unabhängig von Gruppen oder Einzelrechten. |

Wichtige Hinweise:
*	Ein Nutzer ohne aktivierten Staff User-Status kann sich nicht am Backend anmelden.
*	Ein Nutzer ohne Gruppen- oder Einzelberechtigungen sieht nach dem Login eine leere Oberfläche.

## Zuweisen von Einzelberechtigungen
Technisch ist es möglich, einem Benutzer Einzelberechtigungen direkt zuzuweisen (unabhängig von Gruppen). Diese Zuweisung geschieht ebenfalls im Tab „Permissions“ eines Benutzers. Allerdings ist diese Vorgehensweise nicht empfehlenswert, da sie die Rechteverwaltung unübersichtlich macht. Besser ist es, alle Rechte über Gruppenrollen zu steuern, damit Änderungen für mehrere Nutzer gleichzeitig greifen.

## Typische Fehler, Hinweise und Best Practices

Typische Ursachen für Fehler während bei der Konfiguration:

| Problem | Ursache | Lösung |
| :--- | :--- | :----------- |
| Nutzer kann sich nicht anmelden | Staff User nicht aktiviert | Checkbox „Staff User“ aktivieren |
| Nach Login ist die Oberfläche leer | Keine Gruppe oder Rechte zugewiesen | Gruppe im Tab „Permissions“ hinzufügen |
| Nutzer hat zu viele Rechte | Direktberechtigungen zusätzlich zu Gruppenrechten | Direktberechtigungen entfernen, nur Gruppen nutzen |
| Änderungen an Gruppenrechten greifen nicht | Cache oder Session noch aktiv | Abmelden und neu einloggen |
| Neuer Nutzer kann Passwort nicht ändern | Passwortänderung durch Richtlinien blockiert | In den Nutzereinstellungen neues Passwort vergeben |

Wir empfehlen die folgenden Best Practices und Hinweise zu beachten:
*	Verwalten Sie Rechte ausschließlich über Gruppenrollen.
*	Erstellen Sie keine doppelten Gruppen mit ähnlichen Berechtigungen.
*	Dokumentieren Sie Änderungen an Nutzer- und Gruppenrechten, insbesondere bei Projekten mit mehreren Administratoren.
*	Entfernen oder deaktivieren Sie nicht mehr benötigte Benutzerkonten.
*	Prüfen Sie regelmäßig die Gruppenmitgliedschaften auf Aktualität.
*	Verwenden Sie für alle Nutzer starke Passwörter (mindestens 8 Zeichen, Kombination aus Buchstaben, Zahlen und Sonderzeichen).
*	Weisen Sie Superuser-Rechte nur vertrauenswürdigen Administratoren zu.
*	Verwenden Sie für Testzwecke separate Testnutzer, nicht produktive Accounts.
