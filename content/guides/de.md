=== start
name: Hier starten
title: Hier starten: welches Werkzeug passt zu dir?
desc: Ein Überblick in zwei Minuten über Spektronautilus: was jedes Werkzeug kann, welches du wählen solltest und was du vor dem Start wissen solltest.
summary: Ein Überblick in zwei Minuten und Hilfe bei der Wahl des Werkzeugs.

## Was ist Spektronautilus {#what}
Spektronautilus ist eine Sammlung kostenloser Werkzeuge für VJs, visuelle Künstler und Musikliebhaber. Alles läuft in deinem Browser. Deine Videos und deine Musik bleiben auf deinem Gerät und werden nie hochgeladen.

## Welches Werkzeug brauche ich? {#which}
- Du hast **einen Song und ein paar Video-Loops** und möchtest ein fertiges Video: [Magic Videomixer](@guides/magic-mixer/).
- Du möchtest **Musikvideos auf einer Party oder einem Event abspielen** und zwei Videos wie ein DJ mischen: [Video DJ](@guides/video-dj/).
- Du möchtest **Loops live spielen** mit Pads, Ebenen und Beat-Effekten: [VJ-Mixer](@guides/vj-mixer/).
- Deine Loops haben das **falsche Format, sind zu groß oder laufen nicht nahtlos**: [Werkzeuge](@guides/tools/).
- Du hast mehrere lange Aufgaben gestartet und willst sie verfolgen: [Warteschlange](@guides/queue/).

## Die Grundlagen {#basics}
- **Browser.** Ein aktuelles Chrome oder Edge auf einem Computer funktioniert am besten. Die Mixer laufen auch in anderen modernen Browsern, aber einige Funktionen (MIDI, Auswahl des Audiogeräts) brauchen Chrome oder Edge.
- **Handy oder Tablet.** Du wirst automatisch zu einer einfacheren Handy-Version jedes Mixers geleitet. Sie hat weniger Funktionen und läuft dafür flüssig.
- **Videoformat.** Nimm mp4 mit H.264. Es spielt überall. Hast du andere Formate, wandle sie mit den [Werkzeugen](@guides/tools/) um.
- **Sprache.** Die Website hat oben rechts eine Sprachauswahl. In den Mixern und Werkzeugen nutzt du den Knopf 🌐.
- **Hell oder dunkel.** Mixer und Werkzeuge haben einen Knopf zum Wechseln des Designs.
- **Erweitert.** Jedes Werkzeug beginnt mit ein paar einfachen Optionen. Die technischen Einstellungen sind unter [[Advanced]] eingeklappt. Du kannst sie ignorieren, bis du sie brauchst.

## Vor deiner ersten Show {#show}
Starte die Prüfung [Bereit für die Show?](@guides/show-check/) auf dem Computer, den du benutzen wirst. In einer Minute sagt sie dir, ob Videoformat, zweiter Bildschirm, Ton und Geschwindigkeit in Ordnung sind. Lies danach, wie du die Seite [ohne Internet nutzbar](@guides/offline-linux/) machst.

> Teste die Werkzeuge und halte einen Plan B bereit. Die Werkzeuge sind neu, probiere also alles zuerst zu Hause aus.

## Hängst du fest? {#stuck}
Sieh in [Hilfe und Fehlersuche](@guides/help/) nach. Du kannst auch unten auf jeder Seite auf **Feedback** drücken und schreiben, was passiert ist.

=== magic-mixer
name: Magic Videomixer
title: Magic Videomixer: aus einem Song und Loops ein Video machen
desc: Füge einen Song und deine Video-Loops hinzu. Der Mixer hört die Musik, findet Takt und Stimmung und schneidet die Loops zu einem fertigen Video zusammen.
summary: Song und Loops hinzufügen und ein fertiges Video bekommen, das der Musik folgt.

## So funktioniert es {#how}
Du gibst dem Mixer einen Musiktitel und einen Ordner mit Video-Loops. Er analysiert die Musik (Tempo, Takt, Drops, ruhige und laute Teile) und deine Loops (Farbe, Helligkeit, Bewegung). Dann schneidet er die Loops so zusammen, dass Wechsel auf den Taktschlag fallen und ähnliche Loops in ähnlichen Teilen des Songs vorkommen.

## Dein erstes Video {#first}
1. **Musik.** Ziehe eine Audiodatei hinein (mp3 funktioniert am besten) oder drücke [[choose file]]. Der Mixer analysiert die Musik und zeigt dann das Tempo.
2. **Video-Loops.** Ziehe Videos oder einen ganzen Ordner hinein. Die Desktop-Version nimmt bis zu 100 Loops. Nahtlose Loops in gleicher Größe funktionieren am besten. Laufen deine Clips nicht sauber im Kreis, korrigiere sie zuerst mit [[Make loops]] in den [Werkzeugen](@guides/tools/).
3. **Mix-Einstellungen.** Drücke [[Recommended]]. Der Mixer sieht sich Musik und Loops an und schlägt eine Stimmung vor. Du kannst die Stimmung auch selbst wählen, zum Beispiel [[Chill]], [[Ambient]] oder [[Groove]]. Danach kannst du noch alles ändern.
4. **Export.** Drücke [[Add to export queue]]. Das Video entsteht, solange die Seite geöffnet ist.

> Der Export läuft in Echtzeit. Ein Titel von 10 Minuten braucht etwa 10 Minuten. Lass den Tab geöffnet und erwarte keinen Ton, während er arbeitet.

## Einstellungen, die man kennen sollte {#settings}
Die meisten Leute brauchen sie nie. Sie stehen in den Bereichen [[Advanced]].
- [[Typical shot length (bars)]] ist, wie lange ein Clip im Bild bleibt, in Takten gerechnet. 4 Takte sind entspannt, 8 sind langsam, 16 bis 32 sind sehr langsam und ambient.
- [[Crossfade length (beats)]] bestimmt, wie weich ein Clip in den nächsten übergeht. 0 ist ein harter Schnitt.
- [[Loops per section]] ist, wie viele Loops sich einen Teil des Songs teilen. 2 ergibt ein ruhiges A-B-A-B.
- [[Style match]] sorgt dafür, dass der nächste Clip dem vorigen ähnelt, damit der Mix fließt.
- [[Layers & looks]] blendet einen zweiten Clip darüber, gibt jedem Abschnitt einen Farbton und lässt das Bild mit der Musik atmen.
- [[Motion & effects]] bringen Beat-Zoom, Wackeln, Helligkeitspuls und Echo-Spuren. Alles ist standardmäßig sanft.
- [[Use every loop]] versucht, alle deine Loops mindestens einmal zu zeigen.
- [[Use CLIP (AI image understanding)]] lässt ein KI-Modell (CLIP) deine Loops ansehen. Beim ersten Mal lädt es etwa 100 bis 150 MB herunter, nutze also WLAN. Danach funktioniert es offline.
- [[Seed (empty = random)]]. Gleicher Seed und gleiche Einstellungen ergeben denselben Mix. Mit [[Versions]] erzeugst du mehrere verschiedene Mixe auf einmal.

## Exportieren und teilen {#export}
- **Format.** MP4 (H.264). Wähle die Größe (960×540, 1280×720 oder 1920×1080), die Bildrate und die Qualität. 8 Mbit/s sind etwa 600 MB für 10 Minuten.
- **Wo ist das Video?** Fertige Videos bleiben in der Seite, bis du sie herunterlädst oder entfernst. [[Storage in this browser]] zeigt, wie viel Platz sie belegen, und [[Delete all stored videos]] leert es.
- [[Upload to Vimeo (optional)]]. Füge dein eigenes Vimeo-Zugriffstoken ein. Es wird nur in deinem Browser gespeichert und nur an Vimeo gesendet. Videos sind standardmäßig privat.
- **Verfolge die Aufgaben** auf der Seite [Warteschlange](@guides/queue/).

## Die Handy-Version {#phone}
Die Handy-Version ist fürs Telefon gemacht. Wähle einen Titel und ein paar Videos, eine Stimmung und ein Format (Quer oder Hoch) und drücke [[Make video]].
- Lass die Seite offen und den Bildschirm an, während das Video entsteht. Schalte auf dem iPhone zuerst den Stromsparmodus aus, weil er die Videowiedergabe stoppt.
- Wenn das Handy kämpft oder die Seite neu lädt, wähle 30 oder 24 Bilder pro Sekunde, eine kleinere Größe, weniger Loops oder einen kürzeren Titel.
- Das intelligente Zuordnen mit KI ist für ein Handy schwer. Schalte es aus, wenn die Seite von selbst neu lädt.
- Wird etwas unterbrochen, bietet die Seite an, das Gespeicherte herunterzuladen ([[Download recovered video]]).

## Tipps {#tips}
- Nutze Loops mit gleicher Größe und Bildrate. Gemischte Größen gehen, aber es wird ruhiger, wenn sie gleich sind.
- Beginne mit 720p. Gehe höher nur, wenn nötig.
- Nicht zufrieden? Drücke [[Recommended]] erneut, ändere die Stimmung oder nimm einen anderen Seed.
- Etwas stimmt nicht? Sieh in [Hilfe und Fehlersuche](@guides/help/) nach.

=== video-dj
name: Video DJ
title: Video DJ: Musikvideos auf zwei Decks mixen
desc: Mixe komplette Musikvideos wie ein DJ, mit zwei Decks, Crossfader, Vorschau, Logo, Text-Plakaten, MIDI und einem sauberen Ausgabefenster für deinen Projektor.
summary: Musikvideos auf zwei Decks mit Crossfader mixen, gemacht für Events.

## Was es ist {#what}
Video DJ hat zwei Decks für Musikvideos (mp4, mov, webm). Bild und Ton werden zusammen gemischt. Du siehst eine Vorschau beider Decks neben dem Ausgang, und ein eigenes Ausgabefenster geht zum Projektor oder Fernseher.

> Das Werkzeug ist für einen Computer mit Chrome oder Edge gemacht. Auf dem Handy bekommst du eine einfachere Version mit zwei Decks, Crossfader, Effekten, Plakaten und einer Möglichkeit, das Bild an einen anderen Bildschirm zu schicken.

## Dein erster Mix {#first}
1. **Videos hinzufügen.** Ziehe Musikvideos auf die Seite oder drücke [[Add files…]]. Namen wie „Künstler - Titel.mp4“ werden zum Plakattext. Ziehe ein Video direkt auf ein Deck, um es sofort zu laden.
2. **Decks laden.** Lege ein Video auf Deck A und eins auf Deck B. Drücke bei beiden Play.
3. **Ausgabefenster öffnen.** Drücke [[Open output window]], ziehe das neue Fenster auf den Projektor und drücke {{F}} für Vollbild. Lass das Steuerfenster während der Show geöffnet.
4. **Mixen.** Bewege den Crossfader von Hand oder drücke [[Mix to other deck (auto fade)]] für eine weiche Überblendung. [[Fade time]] bestimmt die Dauer.

## Auto-Mix {#automix}
Schalte [[Auto-mix to the next track]] ein, und der Mixer startet den nächsten Titel auf dem freien Deck für dich, einige Sekunden bevor der laufende endet. Die Anzahl bestimmst du. Nutze es für lange Sets oder wenn du eine Pause brauchst.

## Ton {#sound}
- [[Sound follows the crossfader]] blendet den Ton zusammen mit dem Bild über.
- [[Smooth (equal power)]] oder [[Linear]] bestimmt die Kurve der Tonüberblendung.
- Ein sanfter Limiter am Master verhindert, dass zwei laute Titel beim Überlappen übersteuern.
- Mit [[Sound output]] wählst du ein anderes Audiogerät (Chrome oder Edge).

## Logo und Plakate {#posters}
- **Logo.** Füge ein PNG mit Transparenz hinzu (das funktioniert am besten). Das Logo sitzt in der oberen rechten Ecke des Bildes. Wähle die Größe und schalte es mit einem Knopf ein und aus.
- **Plakate.** Ein Plakat ist gleitender Text mit einer großen und einer kleinen Zeile. Wähle eine Farbvorgabe, von wo es hereingleitet und wie lange es bleibt. Speichere Plakate in Plätzen und zeige sie mit einem Klick oder einer Taste.
- **Titelname.** Schalte [[Show the track name when a track mixes in]] ein, dann erscheint das Plakat von selbst.

## MIDI-Controller {#midi}
Schließe deinen Controller an, drücke [[Enable MIDI]] (Chrome oder Edge am Computer), drücke [[Learn]] neben einer Funktion und bewege den Regler, den du verwenden willst.

## Aufnehmen und streamen {#record}
- [[● Record]] speichert den Mix, Bild und Ton, in einer Datei.
- Zum Streamen nimmst du das Ausgabefenster in OBS auf (Window Capture) oder nutzt Chromes „Cast…“ und wählst das Ausgabefenster. Der Mixer schickt selbst kein Video über das Internet.

## Gebaut, um nicht abzustürzen {#safe}
- Titel werden vor dem Abspielen komplett in den Speicher geladen (Dateien über 1,5 GB werden stattdessen gestreamt), die Festplatte kann also keinen Titel unterbrechen.
- Ein Problem mit einer Datei zeigt eine Meldung und stoppt nie das andere Deck.
- Das Bild läuft weiter, wenn das Steuerfenster im Hintergrund ist, und beim versehentlichen Schließen des Fensters wird vorher gefragt.
- Starte vor jedem Event die Prüfung [Bereit für die Show?](@guides/show-check/).

## Die Handy-Version {#phone}
Zwei Decks, Crossfader, Effekte (Zoom, Flash, Strobe, Invert, Mirror), Plakate und Vollbild. Um das Bild auf einem anderen Bildschirm zu zeigen, öffne [[Send to another screen]]: Erzeuge einen Code, öffne den Link auf dem anderen Bildschirm (Laptop, Fernseher-Browser oder Projektor-Rechner im selben WLAN) und füge den Antwortcode ein. Nichts läuft über einen Server.

> Blinkende Effekte können bei manchen Menschen Anfälle auslösen. Halte sie bei öffentlichen Events langsam.

=== vj-mixer
name: VJ-Mixer
title: VJ-Mixer: Loops live mit Pads und Ebenen spielen
desc: Spiele deine Loops live. Zwei Kanäle mit je drei Ebenen, 20 Loop-Pads, Crossfader und Beat-Effekte, die dem Tempo folgen.
summary: Loops live auf 20 Pads spielen, mit Ebenen, Crossfader und Beat-Effekten.

## Was es ist {#what}
Der VJ-Mixer dient dazu, kurze Video-Loops live zu spielen. Du hast 20 Pads, zwei Kanäle (A und B) mit je drei Ebenen, einen Crossfader und einfache Effekte, die dem Beat folgen. Loops laufen ohne Ton.

> Er ist für einen Computer mit Chrome oder Edge gemacht. Auf dem Handy bekommst du eine kleinere Version mit 8 Pads und 2 Ebenen pro Kanal.

## Pads füllen {#pads}
Ziehe Loop-Dateien auf das Pad-Raster oder drücke [[Add loops…]]. Sie füllen die leeren Pads. Nimm mp4-Loops (H.264) für die flüssigste Wiedergabe. Um sie beim nächsten Mal wiederzuverwenden, schalte [[Remember my loops on this computer]] ein. Sie werden nur in diesem Browser gespeichert.

## Spielen {#play}
1. **Ebene wählen.** Jeder Kanal hat drei Ebenen. Wähle die Ebene, auf der du spielen willst.
2. **Drücke ein Pad** (oder seine Taste auf der Tastatur). Der Loop startet sofort auf der gewählten Ebene.
3. **Ebenen mischen.** Jede Ebene hat ihre eigene Deckkraft und einen Mischmodus: normal, add, screen oder multiply.
4. **Kanäle mischen.** Nutze den Crossfader oder [[Mix to other channel (auto fade)]]. [[Clear layer]] leert eine Ebene.

## Der Beat {#beat}
Die Effekte folgen einem Beat. Du kannst ihn auf drei Arten festlegen:
- **Tippe** mehrmals auf die Tempo-Taste oder gib die **BPM** ein.
- Lass den Mixer die **Bassdrum hören**, über einen Audioeingang ([[Audio input (kick drum)]]). Feinjustiere mit [[Sensitivity]].
- Drücke [[Set beat 1 (downbeat)]] in dem Moment, der als erster Schlag eines Taktes zählen soll.

## Beat-Effekte {#effects}
Zoom, Shake, Flash, Strobe, Invert, Mirror, Colour spin und Blur. Schalte jeden einzeln ein, wähle, wie oft er pulsiert (jeden Schlag, alle 2 Schläge oder alle 4 Schläge) und wie stark.

> Flash, Strobe und Invert bei schnellem Tempo können bei manchen Menschen Anfälle auslösen. Halte es bei öffentlichen Events langsam.

## Logo, Plakate, MIDI und Ausgabe {#more}
Das funktioniert wie im [Video DJ](@guides/video-dj/#posters): ein Logo, gleitende Text-Plakate, MIDI-Steuerung mit [[Learn]] und ein Ausgabefenster für den Projektor ({{F}} für Vollbild). Zum Streamen nimmst du das Ausgabefenster in OBS auf oder nutzt Chromes „Cast…“.

## Die Handy-Version {#phone}
8 Pads, zwei Ebenen pro Kanal, Crossfader und Effekte, mit denselben Beat-Werkzeugen. Auch hier laufen Loops ohne Ton.

## Loops zu schwer? {#heavy}
Nimm mp4 (H.264) in 720p oder 1080p. Wandle andere Formate um und verkleinere große Dateien mit den [Werkzeugen](@guides/tools/). Starte [Bereit für die Show?](@guides/show-check/), um zu sehen, wie flüssig dein Computer läuft.

=== tools
name: Loop-Werkzeuge
title: Loop-Werkzeuge: umwandeln, reparieren, filtern und ordnen
desc: Kostenlose Browser-Werkzeuge für VJ-Loops: GIF und Video umwandeln, nahtlose Loops machen, zuschneiden, Größen ändern, Looks hinzufügen, freie Loops finden und Pakete bauen.
summary: Video-Loops umwandeln, loopen, zuschneiden, filtern, finden und verpacken.

## So funktionieren die Werkzeuge {#how}
Öffne die Werkzeuge und wähle eins aus der Liste. Alle folgen demselben Muster:
1. **Dateien hinzufügen.** Ziehe Dateien oder einen Ordner hinein oder drücke [[choose files]].
2. **Einstellungen.** Ein paar einfache Optionen. Die technischen Einstellungen stehen unter [[Advanced]].
3. **Start.** Die Arbeit wird zu Aufgaben in einer Liste. Du kannst viele Dateien einreihen und es laufen lassen. Siehe [Warteschlange](@guides/queue/).
4. **Herunterladen.** Die Ergebnisse sind normale mp4-Dateien, die du in jeder VJ-Software nutzen kannst.

Alles läuft in deinem Browser und deine Dateien verlassen nie deinen Computer. Große Dateien sind kein Problem, sie werden direkt von der Festplatte gelesen. In Chrome oder Edge kannst du auch einen Ordner wählen und jedes Ergebnis direkt dort speichern ([[Save each file straight into a folder I choose]]).

> Die Browser-Version ist langsamer als ein Desktop-Programm (etwa 5- bis 10-mal). Für viele große 4K-Dateien nimm die [Linux-Version](@guides/offline-linux/#linux), die den schnellen Motor auf deinem eigenen Computer nutzt.

## GIF to MP4 {#gif2mp4}
Wandelt viele GIFs auf einmal in flüssiges mp4 um, auch GIFs mit Transparenz. Für transparente GIFs wählst du eine Hintergrundfarbe (schwarz, weiß oder #rrggbb). [[Keep shape, only shrink]] hält kleine GIFs klein. [Dieses Werkzeug öffnen](@@tools/app/#gif2mp4).

## Make loops {#loop}
Prüft, ob ein Clip schon als Loop läuft. Falls ja, bleibt er unverändert. Falls nicht, kann er auf den besten Loop-Punkt gekürzt, vorwärts und dann rückwärts abgespielt oder mit einer Überblendung vom Ende in den Anfang geführt werden. [[Auto: keep good loops, otherwise fix them]] wählt für dich: gute Loops behalten, die anderen reparieren. Du kannst auch eine Mindestlänge festlegen, denn der Magic Videomixer mag Loops ab 16 Sekunden. [Dieses Werkzeug öffnen](@@tools/app/#loop).

## Convert {#convert}
Wandelt mov, webm, mkv, gif und andere Formate in VJ-freundliches mp4 um. Wähle Größe, Bildrate und Qualität und nutze eine [[Name template]], um viele Dateien auf einmal umzubenennen. Die Vorlage versteht Platzhalter wie `{name}`, `{n}`, `{n2}` (eine Zahl mit zwei Stellen), `{w}`, `{h}`, `{res}`, `{fps}`, `{dur}` und `{date}`. Du kannst auch Leerzeichen entfernen, Kleinbuchstaben nutzen und æøå ersetzen. [Dieses Werkzeug öffnen](@@tools/app/#convert).

## Find loops {#search}
Durchsuche freie Quellen nach Loops und lade sie in einem Schritt herunter und wandle sie um. Internet Archive, Wikimedia Commons, NASA und die Prelinger Archives funktionieren ohne Konto. Pexels und Pixabay haben viele fertige Loops, brauchen aber einen kostenlosen Schlüssel, den du in einer Minute bekommst. Der Schlüssel wird nur in deinem Browser gespeichert und nur an diese Seite gesendet.
- Urheber und Lizenz jedes Downloads werden in einer Datei namens `credits.csv` gespeichert. Lizenzen unterscheiden sich je Clip, prüfe sie also, bevor du einen Clip öffentlich nutzt.
- Manche Seiten erlauben einer Webseite nicht, ihre Dateien herunterzuladen. Nutze dann [[Open page]], lade den Clip selbst herunter und ziehe ihn in [[Convert]].
- Lade nur herunter, was du nutzen darfst.

[Dieses Werkzeug öffnen](@@tools/app/#search).

## Filters {#filters}
Fügt einem ganzen Ordner voller Loops VJ-typische Looks hinzu: Glow, Glitch, Spiegel, Kaleidoskop, VHS, Duotone, Pixel, Spuren und mehr. Drücke [[Preview on first clip]], um jeden Look vor dem Anwenden zu sehen. Jede Datei bekommt pro gewähltem Look einen neuen Clip. [Dieses Werkzeug öffnen](@@tools/app/#filters).

## Crop & trim {#crop}
Schneidet Clips auf Breitbild, Hochformat oder Quadrat zu und kürzt Anfang und Ende, für einen ganzen Ordner auf einmal. Wähle, wie es passen soll: exakt auf den Rahmen zuschneiden oder mit schwarzen Balken auffüllen. [Dieses Werkzeug öffnen](@@tools/app/#crop).

## Sizes {#sizes}
Erzeugt von jedem Clip auf einmal einen kleinen Proxy, 720p, 1080p und 4K. Größen, die größer als das Original sind, werden übersprungen. [Dieses Werkzeug öffnen](@@tools/app/#sizes).

## HAP / ProRes {#pro}
Erzeugt professionelle Formate für Resolume, VDMX, Millumin und Videoschnitt. Dafür brauchst du die lokale [Linux-Version](@guides/offline-linux/#linux), weil sie ffmpeg auf deinem eigenen Computer nutzt. [Dieses Werkzeug öffnen](@@tools/app/#pro).

## Catalogue {#catalog}
Erstellt eine Webseite und eine Tabellendatei mit Bild, Länge, Größe und Loop-Qualität jedes Loops. Praktisch für große Sammlungen. [Dieses Werkzeug öffnen](@@tools/app/#catalog).

## Loop pack {#pack}
Bündelt Loops zu einer zip-Datei zum Teilen, mit Vorschaubild, Infodatei und Lizenz. [Dieses Werkzeug öffnen](@@tools/app/#pack).

## Gut zu wissen {#know}
- Loops haben normalerweise keinen Ton. [[Keep sound]] ist standardmäßig aus.
- Kurze Loops ergeben flüssiges Scrubben und Loopen in VJ-Software.
- Wenn etwas fehlschlägt, zeigt die Aufgabe den Grund. Siehe [Hilfe und Fehlersuche](@guides/help/).

=== queue
name: Warteschlange
title: Warteschlange: alle Aufgaben an einem Ort verfolgen
desc: Die Seite Warteschlange zeigt alle Aufgaben aus den Werkzeugen und den Magic Videomixern in einer Liste, damit du lange Exporte verfolgen und die Ergebnisse herunterladen kannst.
summary: Alle Aufgaben aus Werkzeugen und Mixern in einer Liste.

## Was die Warteschlange ist {#what}
Jede lange Arbeit, etwa 200 Dateien umwandeln oder ein 10-Minuten-Video exportieren, wird zu einer Aufgabe. Die Seite Warteschlange zeigt alle Aufgaben der Werkzeuge und beider Magic Videomixer an einem Ort, mit ihrem Status: wartet, läuft, fertig oder fehlgeschlagen.

## So benutzt du sie {#use}
1. Starte Aufgaben in einem Werkzeug oder im Magic Videomixer.
2. Öffne die [Warteschlange](@@queue/) im Menü oben. Eine kleine Zahl neben „Warteschlange“ zeigt, wie viele Aufgaben gerade laufen.
3. Lade fertige Dateien aus der Liste herunter, wenn sie bereit sind.
4. Drücke [[Clear finished]], um aufzuräumen.

> Aufgaben laufen in der Seite, die sie gestartet hat. **Lass diese Seite geöffnet**, bis „fertig“ dasteht. Die Seite Warteschlange ist ein Fenster auf die Aufgaben, sie führt sie nicht aus.

## Wo landen die Dateien? {#files}
Fertige Dateien aus den Werkzeugen werden in diesem Browser gespeichert, bis zu etwa 600 MB pro Aufgabe, damit du sie später herunterladen kannst. Der Magic Videomixer behält seine eigenen Videos auf seiner eigenen Seite, nutze also [[Open page]] in der Warteschlange, um sie herunterzuladen. Nichts verlässt deinen Computer.

Ist eine Datei nicht mehr gespeichert, sagt die Warteschlange das, und du kannst die Aufgabe erneut ausführen.

=== show-check
name: Bereit für die Show?
title: Bereit für die Show? Prüfe dein Gerät, bevor du live gehst
desc: Eine Prüfung in einer Minute für deinen Computer und Browser vor einem Event: Videoformat, zweiter Bildschirm, Ton, Akku, Geschwindigkeit und mehr.
summary: Eine Prüfung deines Geräts in einer Minute, bevor du live gehst.

## Was es ist {#what}
In Video DJ, im VJ-Mixer und in den Handy-Versionen findest du [[Ready for the show?]]. Es prüft dein Gerät und deinen Browser in einer Minute und sagt dir, was du richten solltest, bevor das Publikum kommt. Nichts wird irgendwohin gesendet.

## So benutzt du es {#use}
1. Öffne den Mixer auf dem Computer, den du beim Event nutzt, mit angeschlossenem Projektor.
2. Öffne [[Ready for the show?]] und lies die Liste. Jede Zeile ist [[OK]], [[Check]], [[Problem]] oder [[Info]].
3. Behebe, was nötig ist, und drücke [[Run the check again]].
4. Drücke [[Show test card]], um zu sehen, ob das Bild zum Projektor passt.

## Was jede Zeile bedeutet {#lines}
- [[Video format]]. Ob der Browser mp4 (H.264) abspielt, was die Mixer am liebsten mögen. Wenn nicht, nutze Chrome, Edge oder Safari oder wandle deine Videos mit den [Werkzeugen](@guides/tools/) um.
- [[Works without internet]]. Ob die Seite für die Nutzung ohne Internet gespeichert ist. Siehe [Ohne Internet und Linux](@guides/offline-linux/).
- [[Screen stays awake]]. Ob der Browser verhindern kann, dass der Bildschirm einschläft. Wenn nicht, schalte Bildschirmschoner und Ruhezustand in den Systemeinstellungen aus.
- [[Pop-up windows]]. Das Ausgabefenster ist ein Pop-up. Blockiert der Browser Pop-ups, kann sich das Ausgabefenster nicht öffnen.
- [[Second screen]]. Ob ein zweiter Bildschirm gefunden wird. Schließe zuerst den Projektor an.
- [[Full screen]] und [[MIDI controller]]. Ob sie verfügbar sind und ob ein Controller angeschlossen ist.
- [[Sound]]. Ob der Ton bereit ist.
- [[Battery]]. Warnt bei niedrigem Akku. Stecke vor der Show das Netzteil an.
- [[Speed]]. Ein kurzer Test, wie viele Bilder pro Sekunde der Bildschirm zeichnen kann. Ist er langsam, schließe andere Tabs und Programme und nutze eine kleinere Bildgröße.
- [[Free space]]. Warnt, wenn wenig Speicherplatz für Aufnahmen frei ist.
- [[Output window]], Loops und Titel. Ob das Ausgabefenster offen ist und ob etwas geladen ist.

## Das Testbild {#card}
[[Show test card]] öffnet ein Bild, das für Projektoren gemacht ist. Siehst du einen runden Kreis, alle vier Ecken und den rosa Rahmen, passt das Bild zum Bildschirm. Drücke {{F}} für Vollbild und {{Esc}} oder klicke, um es zu schließen.

## Mit einem Bericht um Hilfe bitten {#report}
[[Copy report]] kopiert eine kurze Zusammenfassung deines Geräts als reinen Text. Füge sie in eine Nachricht ein, wenn du mit dem Knopf **Feedback** um Hilfe bittest, siehe [Hilfe](@guides/help/#feedback).

=== offline-linux
name: Ohne Internet und Linux
title: Spektronautilus ohne Internet nutzen, installieren und unter Linux ausführen
desc: So funktioniert die Seite am Veranstaltungsort ohne Internet, wie du sie wie eine App installierst und die ganze Seite lokal unter Linux für mehr Tempo und Stabilität ausführst.
summary: Ohne Internet arbeiten, die Seite wie eine App installieren oder lokal unter Linux ausführen.

## Ohne Internet arbeiten {#offline}
Spektronautilus speichert sich in deinem Browser, funktioniert also auch ohne WLAN am Veranstaltungsort.
1. Öffne die Seite einmal, solange du online bist.
2. Warte eine Minute. Die Seiten und die Mixer werden gespeichert.
3. Starte [[Ready for the show?]] und sieh dir die Zeile [[Works without internet]] an.

Du kannst die Seite auch als App **installieren**: Nutze „Installieren“ oder „Zum Startbildschirm hinzufügen“ im Browsermenü. Sie öffnet sich dann in einem eigenen Fenster.

> Die Werkzeuge laden ihre Video-Engine (etwa 30 MB) beim ersten Benutzen. Benutze jedes Werkzeug einmal, solange du online bist. Die Linux-Version braucht diese Engine nicht.

## Updates {#updates}
Wenn eine neue Version bereit ist, sagt eine kleine Leiste [[A new version is ready.]] mit den Knöpfen [[Update now]] und „Später“. Sie aktualisiert nie von selbst, während die Seite offen ist, sodass eine laufende Show nie gestört wird. Aktualisiere vor dem Event, nicht währenddessen.

## Linux-Version {#linux}
Es gibt eine Version, die die ganze Seite auf deinem eigenen Linux-Computer ausführt. Sie ist nur von deinem Computer aus erreichbar (Adresse 127.0.0.1) und öffnet sich in Chrome oder Chromium in einem eigenen Fenster, gestartet mit Einstellungen für Live-Visuals.

Warum sie nutzen:
- **Tempo.** Ist `ffmpeg` installiert, nutzen die Werkzeuge es statt der langsameren Browser-Engine. Die Seite zeigt dann „Fast mode“.
- **Keine Speichergrenze** für große Dateien, und kein Internet nötig (nur [[Find loops]] braucht es).
- **HAP und ProRes.** Das [HAP / ProRes-Werkzeug](@guides/tools/#pro) funktioniert in der Linux-Version.

So installierst du sie:
1. Lade das Linux-Paket (`spektronautilus-linux.tar.gz`) herunter und entpacke es: `tar xzf spektronautilus-linux.tar.gz`.
2. Wechsle in den Ordner und führe `./install.sh` aus. Es braucht keine Root-Rechte. Es legt einen Menüeintrag und den Befehl `spektronautilus` an, mit Verknüpfungen zu Video DJ, VJ-Mixer und den Loop-Werkzeugen.
3. Zum Ausprobieren ohne Installation führst du `./spektronautilus.py` im entpackten Ordner aus.
4. `./uninstall.sh` entfernt es wieder.

Du brauchst Python 3.8 oder neuer und, für die Mixer, Chrome oder Chromium. Für ffmpeg unter Debian oder Ubuntu führe `sudo apt install ffmpeg` aus.

## Sicher von Grund auf {#safe}
Der lokale Server nimmt nur Anfragen von deinem eigenen Computer an, lehnt andere Website-Namen ab und lässt ffmpeg nur seinen eigenen temporären Ordner berühren, der beim Beenden gelöscht wird.

=== help
name: Hilfe und Fehlersuche
title: Hilfe und Fehlersuche: wenn etwas nicht funktioniert
desc: Antworten auf häufige Probleme: Videos, die nicht spielen, das Ausgabefenster, Ruckeln, ein Handy, das neu lädt, MIDI, verlorene Dateien und wie du Kontakt aufnimmst.
summary: Antworten auf häufige Probleme und wie du Kontakt aufnimmst.

## Ein Video spielt nicht {#play}
Fast immer ein Formatproblem. Die Mixer mögen **mp4 mit H.264**. Wandle die Datei mit [[Convert]] in den [Werkzeugen](@guides/tools/) um. iPhone-Videos in HEVC, manche mov-Dateien und webm-Dateien können in manchen Browsern Probleme machen.

## Es kommt kein Ton {#sound}
- Loops im VJ-Mixer laufen absichtlich ohne Ton.
- Prüfe im Video DJ die Lautstärke des Decks, den Master und [[Sound follows the crossfader]].
- Der Browser braucht vielleicht einen Klick auf die Seite, bevor er Ton abspielt. Klicke einmal auf die Seite.
- Prüfe [[Sound output]], wenn du mehr als ein Audiogerät nutzt.

## Das Ausgabefenster öffnet sich nicht {#output}
Der Browser hat das Pop-up blockiert. Erlaube Pop-ups für die Seite und versuche es erneut. Die Prüfung [Bereit für die Show?](@guides/show-check/) testet das.

## Das Bild ruckelt {#stutter}
- Wähle eine kleinere Bildgröße (die Ausgabegröße) und nutze Loops in 720p.
- Schließe andere Tabs und Programme.
- Nutze ein aktuelles Chrome oder Edge und stecke den Computer an.
- Mache den Geschwindigkeitstest in [Bereit für die Show?](@guides/show-check/).
- Stelle am Laptop sicher, dass der Browser die starke Grafikkarte nutzt.

## Mein Handy lädt die Seite neu {#phone}
Dem Handy ging der Speicher aus oder der Bildschirm hat sich gesperrt. Nimm eine kleinere Größe, 30 oder 24 Bilder pro Sekunde, weniger oder kürzere Loops und lass den Bildschirm an. Schalte auf dem iPhone den Stromsparmodus aus. Schalte im Magic Videomixer das intelligente Zuordnen mit KI aus.

## Der Export ist stehen geblieben oder sehr langsam {#export}
Exporte laufen in Echtzeit, ein Titel von 10 Minuten braucht also etwa 10 Minuten. Lass den Tab offen und sichtbar und lass den Computer nicht schlafen. Wurde er unterbrochen, bietet der Magic Videomixer an, das Gespeicherte zu retten.

## MIDI findet meinen Controller nicht {#midi}
Nutze Chrome oder Edge an einem Computer. Schließe zuerst den Controller an, drücke dann [[Enable MIDI]] und erlaube es im Browser. Andere Programme, die den Controller nutzen, können ihn blockieren, schließe sie also.

## Wo sind meine Dateien? {#files}
In deinem Browser, auf deinem Computer. Fertige Ergebnisse der Werkzeuge und Videos des Magic Videomixers stehen auf der Seite [Warteschlange](@guides/queue/). Löschst du die Website-Daten deines Browsers, sind sie weg. Lade also herunter, was du behalten willst.

## Datenschutz {#privacy}
Keine Konten und kein Tracking. Videos und Musik werden auf deinem Gerät verarbeitet. Die Suche nach Loops kontaktiert die gewählten Videoquellen, und der optionale Vimeo-Upload kontaktiert Vimeo.

## Kontakt aufnehmen {#feedback}
Drücke den Knopf **Feedback** unten auf jeder Seite und schreibe, was passiert ist. Er öffnet dein E-Mail-Programm mit der fertigen Nachricht. Schreibe dazu, welchen Browser du nutzt und was du gerade getan hast. Bei einem Problem auf einem Show-Computer füge den Bericht aus [Bereit für die Show?](@guides/show-check/#report) bei. Du kannst uns auch auf [GitHub](https://github.com/munkenbissniss/spektronautilus/issues) schreiben.
