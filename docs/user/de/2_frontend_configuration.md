# Konfiguration der Frontend-Darstellung
## Zweck und Überblick
Über die Administrationsoberfläche des LauterWissens kann das Erscheinungsbild und die Struktur der Kartenansicht im Frontend dynamisch angepasst werden.
Dies ermöglicht es, Inhalte, Layer und Objektattribute zu konfigurieren, ohne Änderungen am Code vornehmen zu müssen.
Die Konfiguration erfolgt über den Menüpunkt „Frontend-Konfiguration“
Hier können insbesondere folgende Elemente während der Laufzeit angepasst werden:
*	Sidebar-Konfiguration: Verwaltung thematischer Gruppen und Kartenebenen
*	Objekt- und Attributkonfiguration: Steuerung, welche Datenfelder in der Kartenansicht oder in Pop-ups angezeigt werden

## Konfiguration der Sidebar
Die Sidebar im Frontend dient der thematischen Gliederung der dargestellten Inhalte. Sie ermöglicht es Nutzenden, zwischen verschiedenen Themenbereichen (z. B. Freizeit, Bildung, Kultur) zu wechseln und Kartenlayer gezielt ein- oder auszublenden.

### Anlegen thematischer Gruppen
Unter dem Reiter „Sidebar“ können neue Kategorien angelegt oder bestehende bearbeitet werden. Für jede Kategorie müssen folgende Informationen angegeben werden:

| Feldname | Beschreibung |
| :-- | :----------- |
| Title	| Bezeichnung der thematischen Gruppe, wie sie im Frontend angezeigt wird |
| Color	| Farbton der Kategorie (alle Objekte der Gruppe werden in der Karte in abgestuften Tönen dieser Farbe angezeigt) |
| Order	| Bestimmt die Anzeigereihenfolge in der Sidebar (aufsteigende Sortierung) |

Hinweis: Farbgruppen dienen nicht nur der visuellen Ordnung, sondern auch der automatischen Farbzuweisung für neue Layer innerhalb dieser Kategorie.

### Hinzufügen von neuen Kartenebenen

Innerhalb jeder Sidebar-Kategorie können über den Abschnitt „Map Layers“ neue Kartenebenen hinzugefügt werden. Für jede Ebene sind folgende Angaben erforderlich:

| Feldname | Beschreibung |
| :-- | :----------- |
| Name | Anzeigename des Layers in der Sidebar
| URL	| Adresse der Datenquelle – entweder 1. REST-Endpunkt des internen Systems oder 2. externe WMS-URL
| Color (optional) |	Spezifische Farbe für diesen Layer, falls diese von der Gruppenfarbe abweichen sollte
| Legend-URL (optional)	| URL-Pfad zu einer Legende (PDF oder Bilddatei)
| Attribution Source / Attribution License / Attribution URL (alle optional) |	Angaben zur Datenquelle und Lizenzinformationen

Unter dem Feld können zwei unterschiedliche Datenquellen für den entsprechenden Layer konfiguriert werden.
Daten aus dem internen System: Für interne Layer wird der entsprechende REST-Endpunkt des Backends angegeben.

Beispiel: `/geo/osmleisuredogpark`

Dieser verweist auf die Daten eines Modells, das unter „Datenmodelle“ gepflegt wird (siehe Abschnitt 4.3).

Externe Layer (WMS): Neben internen Daten können auch externe WMS-Dienste eingebunden werden. Dies ermöglicht die Integration von Geodaten öffentlicher Dienste (z.B. Stadtplanung, Open Data-Portale). Die Konfiguration dieser Datenquelle wird im nächsten Abschnitt näher erläutert.

### Hinzufügen von neuen WMS-Layern

Das Hinzufügen eines neuen WMS-Layers wird im Folgenden anhand eines realen Beispiels aufgezeigt. Zur Konfiguration eine WMS-Layers neben dem Namen die Erzeugung der entsprechenden URL relevant. Diese setzt sich wie folgt zusammen:
`$WMS_ENDPUNKT&SERVICE=WMS&layername=$LAYERNAME`
Dabei ist der Endpunkt (`$WMS_ENDPUNKT`) und der Layer-Namen gemäß der WMS-Service Beschreibung (`$LAYERNAME`) anzugeben. Der Parameter `&SERVICE=WMS` ist ebenfalls verpflichtend (fix) anzugeben.

Beispiel: Integration eines WMS-Layers der Stadt Kaiserslautern

1.	GetCapabilities-Abfrage durchführen: Rufen Sie den Capabilities-Endpunkt des gewünschten WMS-Dienstes auf. Z. B. für dieses Beispiel:
`https://geoportal.kaiserslautern.de/cgi-bin/fnpkl?REQUEST=GetCapabilities&SERVICE=WMS`

2.	Layer-Namen auslesen: Im XML-Ergebnis suchen Sie den Eintrag unter Layer und wählen den entsprechenden Layer-Namen aus, z.B. (`FNP_Stadt_Kaiserslautern`):

```bash
...
<Layer>
  <Name>FNP_Stadt_Kaiserslautern</Name>
</Layer>
...
```

3.	Endpunkt / OnlineResource auslesen: In dem XML- Ergebnis befindet sich der Endpunkt des Dienstes (`https://geoportal.kaiserslautern.de/cgi-bin/fnpkl?`):
```bash
...
<OnlineResource xlink:href="https://geoportal.kaiserslautern.de/cgi-bin/fnpkl?" />
...
```

4.	Layer im Backend hinzufügen
*	Öffnen Sie in der Administrationsoberfläche den Bereich Frontend-Konfiguration → Sidebar
*	Wählen Sie eine bestehende Kategorie oder legen Sie eine neue an
*	Fügen Sie einen neuen Layer hinzu und tragen Sie die Werte wie folgt ein:

| Feld | Wert |
| :-- | :----------- |
| Name |	Flächennutzungsplan |
| URL	| `https://geoportal.kaiserslautern.de/cgi-bin/fnpkl?SERVICE=WMS&layer=FNP_Stadt_Kaiserslautern` |
| Quelle / Lizenz / URL / Legende | Optionale Angaben sofern in der XML-Dienstbeschreibung vorhanden |

### Erweiterte Einstellungen pro Layer

Für jede Kartenebene können zusätzlich folgende Optionen gesetzt werden:

*	Legenden-URL: Verknüpft eine externe oder lokale Grafik- oder PDF-Datei mit dem Layer.
*	Legenden Attributionen: Angaben zur Datenquelle, Urheber und Lizenzbedingungen (werden im Frontend in der Kartenlegende angezeigt).
*	Farbüberschreibungen: Weist einer Ebene explizit eine Farbe zu, unabhängig von der übergeordneten Kategorie. Diese Funktion ist besonders nützlich, um z.B. bestimmte Layer (wie Bäume oder Infrastrukturobjekte) farblich hervorzuheben.

## Konfiguration der Objekt- und Attributdarstellung

Unter dem Reiter „Datenmodell“ können die in der Karte dargestellten Objekte und deren Attribute angepasst werden. In der Ansicht werden alle verfügbaren Modelle (Tabellen) aufgelistet, die über Schnittstellen oder Pipelines befüllt werden.

### Übersicht der Datenmodelle

Die Übersicht zeigt pro Modell:
*	den internen Datenbanknamen (z. B. osmleisuredogpark),
*	den REST-Endpunkt (z. B. /geo/osmleisuredogpark),
*	den Anzeigenamen, der im Frontend verwendet wird (z. B. „Hundewiese“).

### Konfiguration der Feldanzeige
Beim Klick auf ein Modell öffnet sich die Detailansicht unter „Field Configurations“.

In der Ansicht kann für jedes Feld (Attribut) des Modells konfiguriert werden:

| Einstellung	| Beschreibung |
| :--- | :----------- |
| Field Name	| Name des Attributes des Objektes |
| Visible	| Gibt an, ob das Attribut im Frontend (z. B. im Pop-up) angezeigt wird |
| Display Name | Anzeigename des Feldes im Frontend |


Beispiel: Das Feld website kann als „Website“ angezeigt werden, während address zu „Adresse“ umbenannt wird.

Hinweis: Wenn ein Feld in der Datenquelle keinen Wert enthält, wird es automatisch ausgeblendet, um leere Zeilen in der Pop-up-Anzeige zu vermeiden.

## Typische Fehler, Hinweise und Best Practices

Typische Ursachen für Fehler während bei der Konfiguration:

		
| Problem | Ursache | Lösung |
| :--- | :--- | :----------- |
| WMS-Layer wird nicht angezeigt | CORS oder falscher Layername	| GetCapabilities prüfen
| Farbe in Karte nicht korrekt |	Überschreibung auf Layer-Ebene aktiv	| Farbdefinition prüfen
| Attribut fehlt im Pop-up | Feld auf „Visible = false“ gesetzt oder leerer Wert | Sichtbarkeit aktivieren bzw. Daten prüfen
| Pop-up zeigt unverständliche Feldnamen |	Feldnamen nicht umbenannt	| Anzeigenamen in Field Configuration anpassen

Wir empfehlen die folgenden Best Practices und Hinweise zu beachten:
*	Gruppieren Sie Layer logisch nach Themen, nicht nach Datenquellen.
*	Nutzen Sie Farbkonventionen konsistent (z.B. Grün für Freizeit, Blau für Bildung).
*	Halten Sie Layer-Beschreibungen und Quellenangaben aktuell.
*	Testen Sie neue WMS-Dienste vor der Freigabe auf Performance und Kompatibilität.
*	Verwenden Sie für Modellattribute kurze, verständliche Anzeigenamen – sie erscheinen direkt in Pop-ups.
*	Dokumentieren Sie Änderungen an Layern und Modellen in einem Changelog oder internen Wiki. Wir empfehlen Ihnen die Änderungen in der Konfigurations-Datei `/config/init/frontend_sidebar_config.json` bzw. einer entsprechenden Kopie nachzupflegen und zu versionieren. Im Falle einer korrupten Datenbank, können die vorgenommenen Änderungen somit jederzeit widerhergestellt oder neu importiert werden.
