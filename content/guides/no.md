=== start
name: Start her
title: Start her: hvilket verktøy passer for deg?
desc: En oversikt på to minutter over Spektronautilus: hva hvert verktøy gjør, hvilket du bør velge og hva du bør vite før du begynner.
summary: En oversikt på to minutter, og hjelp til å velge verktøy.

## Hva er Spektronautilus {#what}
Spektronautilus er en samling gratis verktøy for VJ-er, visuelle kunstnere og musikkelskere. Alt kjører i nettleseren din. Videoer og musikk blir på din egen enhet og lastes aldri opp.

## Hvilket verktøy trenger jeg? {#which}
- Du har **en sang og noen videoloops** og vil ha en ferdig video: [Magisk videomikser](@guides/magic-mixer/).
- Du vil **spille musikkvideoer på fest eller arrangement** og mikse to videoer som en DJ: [Video DJ](@guides/video-dj/).
- Du vil **spille loops live** med pads, lag og beat-effekter: [VJ-mikser](@guides/vj-mixer/).
- Loopene dine har **feil format, er for store eller går ikke sømløst rundt**: [Verktøy](@guides/tools/).
- Du har startet flere lange jobber og vil følge med: [Kø](@guides/queue/).

## Det grunnleggende {#basics}
- **Nettleser.** Nyeste Chrome eller Edge på en datamaskin fungerer best. Mikserne fungerer også i andre moderne nettlesere, men noen funksjoner (MIDI, valg av lydenhet) krever Chrome eller Edge.
- **Mobil eller nettbrett.** Du sendes automatisk til en enklere mobilversjon av hver mikser. Den har færre funksjoner, så den går jevnt.
- [[Video format]]. Bruk mp4 med H.264. Det spilles av overalt. Har du andre formater, konverterer du dem med [Verktøy](@guides/tools/).
- **Språk.** Nettsiden har språkvalg øverst til høyre. Inne i miksere og verktøy bruker du 🌐-knappen.
- **Lyst eller mørkt.** Miksere og verktøy har en knapp for å bytte tema.
- **Avansert.** Hvert verktøy starter med noen få enkle valg. De tekniske innstillingene ligger gjemt under [[Advanced]]. Du kan se bort fra dem til du trenger dem.

## Før det første showet {#show}
Kjør sjekken [Klar for showet?](@guides/show-check/) på datamaskinen du skal bruke. Den forteller deg på et minutt om videoformat, ekstra skjerm, lyd og hastighet er i orden. Les deretter hvordan du gjør siden [brukbar uten internett](@guides/offline-linux/).

> Test verktøyene og ha en plan B klar. Verktøyene er nye, så prøv alt hjemme først.

## Står du fast? {#stuck}
Se [Hjelp og feilsøking](@guides/help/). Du kan også trykke på **Tilbakemelding**-knappen nederst på alle sider og fortelle hva som skjedde.

=== magic-mixer
name: Magisk videomikser
title: Magisk videomikser: lag en video av en sang og noen loops
desc: Legg til en sang og videoloopene dine. Mikseren lytter til musikken, finner takten og stemningen, og klipper loopene sammen til en ferdig video.
summary: Legg til en sang og noen loops, og få en ferdig video som følger musikken.

## Slik fungerer den {#how}
Du gir mikseren ett musikkspor og en mappe med videoloops. Den analyserer musikken (tempo, takt, drop, rolige og høye partier) og loopene dine (farge, lysstyrke, bevegelse). Så klipper den loopene sammen slik at byttene faller på taktslagene og like loops brukes i like deler av sangen.

## Lag din første video {#first}
1. **Musikk.** Slipp én lydfil (mp3 fungerer best), eller trykk [[choose file]]. Mikseren analyserer musikken og viser deretter tempoet.
2. **Videoloops.** Slipp videoer eller en hel mappe. Desktop-versjonen tar opptil 100 loops. Sømløse loops i samme størrelse fungerer best. Hvis klippene ikke går jevnt rundt, fikser du dem først med [[Make loops]] i [Verktøy](@guides/tools/).
3. **Miksinnstillinger.** Trykk [[Recommended]]. Mikseren ser på musikken og loopene og foreslår en stemning. Du kan også velge stemning selv, for eksempel [[Chill]], [[Ambient]] eller [[Groove]]. Du kan fortsatt endre alt etterpå.
4. **Eksport.** Trykk [[Add to export queue]]. Videoen lages mens siden er åpen.

> Eksporten går i sanntid. Et spor på 10 minutter tar omtrent 10 minutter. Ha fanen åpen, og ikke forvent lyd mens den jobber.

## Innstillinger det er greit å kjenne til {#settings}
De fleste trenger dem aldri. De ligger under [[Advanced]].
- [[Typical shot length (bars)]] er hvor lenge et klipp står på skjermen, målt i takter. 4 takter er avslappet, 8 takter er rolig, 16 til 32 takter er veldig rolig og ambient.
- [[Crossfade length (beats)]] bestemmer hvor mykt ett klipp smelter over i det neste. 0 er et hardt kutt.
- [[Loops per section]] er hvor mange loops som deler en del av sangen. 2 gir en rolig A-B-A-B.
- [[Style match]] gjør at neste klipp ligner på det forrige, så miksen flyter.
- [[Layers & looks]] legger et klipp til oppå, gir hver del en fargetone og lar bildet puste med musikken.
- [[Motion & effects]] gir beat-zoom, risting, lyspuls og ekko-spor. Alt er behagelig som standard.
- [[Use every loop]] prøver å vise alle loopene minst én gang.
- [[Use CLIP (AI image understanding)]] lar en KI-modell (CLIP) se på loopene dine. Den laster ned ca. 100 til 150 MB første gang, så bruk Wi-Fi. Etter det fungerer den uten internett.
- [[Seed (empty = random)]]. Samme seed og samme innstillinger gir samme miks. Bruk [[Versions]] for å lage flere ulike miksere på en gang.

## Eksporter og del {#export}
- **Format.** MP4 (H.264). Velg størrelse (960×540, 1280×720 eller 1920×1080), bildefrekvens og kvalitet. 8 Mbit/s blir ca. 600 MB per 10 minutter.
- **Hvor er videoen?** Ferdige videoer blir liggende i siden til du laster dem ned eller fjerner dem. [[Storage in this browser]] viser hvor mye plass de bruker, og [[Delete all stored videos]] tømmer det.
- **Last opp til Vimeo (valgfritt).** Lim inn ditt eget Vimeo-token. Det lagres bare i nettleseren din og sendes bare til Vimeo. Videoer er private som standard.
- **Følg jobbene** på [Kø](@guides/queue/)-siden.

## Mobilversjonen {#phone}
Mobilversjonen er laget for telefon. Velg et spor og noen videoer, velg stemning og format (liggende eller stående) og trykk [[Make video]].
- Ha siden åpen og skjermen på mens videoen lages. På iPhone må du slå av Lavstrømmodus først, fordi den stopper avspilling av video.
- Hvis telefonen sliter eller siden laster på nytt, velg 30 eller 24 bilder per sekund, mindre størrelse, færre loops eller kortere spor.
- [[Smarter matching (AI)]] er tungt for en telefon. Slå den av hvis siden laster på nytt av seg selv.
- Hvis noe blir avbrutt, tilbyr siden å laste ned det som ble lagret ([[Download recovered video]]).

## Tips {#tips}
- Bruk loops med samme størrelse og bildefrekvens. Blandede størrelser fungerer, men det blir roligere når de er like.
- Begynn med 720p. Gå høyere bare når du trenger det.
- Ikke fornøyd? Trykk [[Recommended]] på nytt, endre stemning eller bruk en annen seed.
- Noe galt? Se [Hjelp og feilsøking](@guides/help/).

=== video-dj
name: Video DJ
title: Video DJ: miks musikkvideoer på to dekk
desc: Miks hele musikkvideoer som en DJ, med to dekk, crossfader, forhåndsvisning, logo, tekstplakater, MIDI og et rent utgangsvindu til projektoren.
summary: Miks musikkvideoer på to dekk med crossfader, laget for arrangementer.

## Hva det er {#what}
Video DJ har to dekk for musikkvideoer (mp4, mov, webm). Bilde og lyd mikses sammen. Du ser en forhåndsvisning av begge dekkene ved siden av utgangen, og et eget utgangsvindu går til projektoren eller TV-en.

> Verktøyet er laget for en datamaskin med Chrome eller Edge. På mobil får du en enklere versjon med to dekk, crossfader, effekter, plakater og en måte å sende bildet til en annen skjerm.

## Din første miks {#first}
1. **Legg til videoer.** Slipp musikkvideoer på siden, eller trykk [[Add files…]]. Navn som «Artist - Tittel.mp4» blir til plakattekst. Slipp en video rett på et dekk for å laste den med en gang.
2. **Last dekkene.** Legg en video på dekk A og en på dekk B. Trykk play på begge.
3. **Åpne utgangsvinduet.** Trykk [[Open output window]], dra det nye vinduet til projektoren og trykk {{F}} for fullskjerm. Ha kontrollvinduet åpent under showet.
4. **Miks.** Flytt crossfaderen for hånd, eller trykk [[Mix to other deck (auto fade)]] for en myk overgang. [[Fade time]] bestemmer hvor lenge den varer.

## Auto-mix {#automix}
Slå på [[Auto-mix to the next track]], så starter mikseren neste spor på det ledige dekket for deg, et antall sekunder før det som spilles er ferdig. Du bestemmer antallet. Bruk det til lange sett, eller når du trenger en pause.

## Lyd {#sound}
- [[Sound follows the crossfader]] fader lyden sammen med bildet.
- [[Smooth (equal power)]] eller [[Linear]] bestemmer kurven på lydfadingen.
- En myk limiter på masteren hindrer at to høye spor klipper når de overlapper.
- [[Sound output]] lar deg velge en annen lydenhet (Chrome eller Edge).

## Logo og plakater {#posters}
- **Logo.** Legg til en PNG med gjennomsiktighet (det fungerer best). Logoen står øverst til høyre i bildet. Velg størrelse, og slå den av og på med én knapp.
- **Plakater.** En plakat er tekst som glir inn, med en stor og en liten linje. Velg fargeforhåndsvalg, hvor den glir inn fra og hvor lenge den blir stående. Lagre plakater i plasser og vis dem med ett klikk eller en tast.
- **Sporets navn.** Slå på [[Show the track name when a track mixes in]], så dukker plakaten opp av seg selv.

## MIDI-kontroller {#midi}
Koble til kontrolleren, trykk [[Enable MIDI]] (Chrome eller Edge på datamaskin), trykk [[Learn]] ved siden av en funksjon og beveg kontrollen du vil bruke.

## Ta opp og strøm {#record}
- [[● Record]] lagrer miksen, bilde og lyd, til en fil.
- For å strømme tar du opp utgangsvinduet i OBS (Window Capture), eller bruker Chromes «Cast…» og velger utgangsvinduet. Mikseren sender ikke video over internett selv.

## Laget for å ikke krasje {#safe}
- Spor lastes helt inn i minnet før de spilles (filer over 1,5 GB strømmes i stedet), så disken kan ikke avbryte et spor.
- Et problem med én fil gir en melding og stopper aldri det andre dekket.
- Bildet fortsetter å gå når kontrollvinduet ligger i bakgrunnen, og hvis du lukker vinduet ved en feil, blir du spurt først.
- Kjør sjekken [Klar for showet?](@guides/show-check/) før hvert arrangement.

## Mobilversjonen {#phone}
To dekk, crossfader, effekter (Zoom, Flash, Strobe, Invert, Mirror), plakater og fullskjerm. For å vise bildet på en annen skjerm åpner du [[Send to another screen]]: lag en kode, åpne lenken på den andre skjermen (en laptop, en TV-nettleser eller en projektor-PC på samme Wi-Fi), og lim inn svarkoden. Ingenting går via en server.

> Blinkende effekter kan utløse anfall hos noen. Hold dem rolige på offentlige arrangementer.

=== vj-mixer
name: VJ-mikser
title: VJ-mikser: spill loops live med pads og lag
desc: Spill loopene dine live. To kanaler med tre lag hver, 20 loop-pads, crossfader og beat-effekter som følger tempoet.
summary: Spill loops live på 20 pads med lag, crossfader og beat-effekter.

## Hva det er {#what}
VJ-mikseren er for å spille korte videoloops live. Du har 20 pads, to kanaler (A og B) med tre lag hver, en crossfader og enkle effekter som følger taktslagene. Loops spilles uten lyd.

> Den er laget for en datamaskin med Chrome eller Edge. På mobil får du en mindre versjon med 8 pads og 2 lag per kanal.

## Fyll padsene {#pads}
Slipp loopfiler på pad-rutenettet, eller trykk [[Add loops…]]. De fyller de tomme padsene. Bruk mp4-loops (H.264) for jevnest avspilling. For å bruke dem igjen neste gang slår du på [[Remember my loops on this computer]]. De lagres bare i denne nettleseren.

## Spill {#play}
1. **Velg et lag.** Hver kanal har tre lag. Velg laget du vil spille på.
2. **Trykk på en pad** (eller tasten den har på tastaturet). Loopen starter med en gang på det valgte laget.
3. **Miks lagene.** Hvert lag har sin egen gjennomsiktighet og en blandingsmodus: normal, add, screen eller multiply.
4. **Miks kanalene.** Bruk crossfaderen, eller [[Mix to other channel (auto fade)]]. [[Clear layer]] tømmer et lag.

## Takten {#beat}
Effektene følger en takt. Du kan sette den på tre måter:
- **Tapp** tempoknappen noen ganger, eller skriv inn **BPM**.
- La mikseren **lytte til basstrommen** gjennom en lydinngang ([[Audio input (kick drum)]]). Juster med [[Sensitivity]].
- Trykk [[Set beat 1 (downbeat)]] i øyeblikket som skal telle som første slag i en takt.

## Beat-effekter {#effects}
Zoom, Shake, Flash, Strobe, Invert, Mirror, Colour spin og Blur. Slå på hver enkelt, velg hvor ofte den pulserer (hvert slag, 2 slag eller 4 slag) og hvor sterk den er.

> Flash, Strobe og Invert i høyt tempo kan utløse anfall hos noen. Hold det rolig på offentlige arrangementer.

## Logo, plakater, MIDI og utgang {#more}
Dette fungerer som i [Video DJ](@guides/video-dj/#posters): logo, tekstplakater som glir inn, MIDI-styring med [[Learn]], og et utgangsvindu til projektoren (trykk {{F}} for fullskjerm). For å strømme tar du opp utgangsvinduet i OBS eller bruker Chromes «Cast…».

## Mobilversjonen {#phone}
8 pads, to lag per kanal, crossfader og effekter, med de samme taktverktøyene. Loops spilles også uten lyd her.

## Er loopene for tunge? {#heavy}
Bruk mp4 (H.264) i 720p eller 1080p. Konverter andre formater og krymp store filer med [Verktøy](@guides/tools/). Kjør [Klar for showet?](@guides/show-check/) for å se hvor jevnt datamaskinen din går.

=== tools
name: Loop-verktøy
title: Loop-verktøy: konverter, fiks, filtrer og organiser loopene dine
desc: Gratis nettleserverktøy for VJ-loops: konverter GIF-er og video, lag sømløse loops, beskjær, endre størrelse, legg på looks, finn gratis loops og lag pakker.
summary: Konverter, loop, beskjær, filtrer, finn og pakk videoloopene dine.

## Slik fungerer verktøyene {#how}
Åpne verktøyene og velg ett fra listen. Alle følger samme mønster:
1. **Legg til filer.** Slipp filer eller en mappe, eller trykk [[choose files]].
2. **Innstillinger.** Noen få enkle valg. De tekniske innstillingene ligger under [[Advanced]].
3. **Start.** Arbeidet blir til jobber i en jobbliste. Du kan legge mange filer i kø og la det gå. Se [Kø](@guides/queue/).
4. **Last ned.** Resultatene er vanlige mp4-filer du kan bruke i all VJ-programvare.

Alt kjører inne i nettleseren din, og filene dine forlater aldri datamaskinen. Store filer går fint, de leses rett fra disken. I Chrome eller Edge kan du også velge en mappe og lagre hvert resultat rett i den ([[Save each file straight into a folder I choose]]).

> Nettleserversjonen er tregere enn et vanlig program (omtrent 5 til 10 ganger). For mange store 4K-filer bruker du [Linux-versjonen](@guides/offline-linux/#linux), som bruker den raske motoren på din egen datamaskin.

## GIF to MP4 {#gif2mp4}
Konverterer mange GIF-er til jevn mp4 på en gang, også GIF-er med gjennomsiktighet. For gjennomsiktige GIF-er velger du bakgrunnsfarge (svart, hvit eller #rrggbb). [[Keep shape, only shrink]] holder små GIF-er små. [Åpne dette verktøyet](@@tools/app/#gif2mp4).

## Make loops {#loop}
Sjekker om et klipp allerede går rundt som en loop. Hvis det gjør det, blir det latt i fred. Hvis ikke kan det trimme klippet til det beste loop-punktet, spille det forover og så bakover, eller krysse enden over i starten. [[Auto: keep good loops, otherwise fix them]] velger for deg: behold gode loops, fiks de andre. Du kan også sette en minstelengde, fordi Magisk videomikser liker loops på 16 sekunder eller mer. [Åpne dette verktøyet](@@tools/app/#loop).

## Convert {#convert}
Gjør mov, webm, mkv, gif og andre formater om til VJ-vennlig mp4. Velg størrelse, bildefrekvens og kvalitet, og bruk [[Name template]] for å gi nytt navn i bulk. Malen kjenner koder som `{name}`, `{n}`, `{n2}` (et tall med to sifre), `{w}`, `{h}`, `{res}`, `{fps}`, `{dur}` og `{date}`. Du kan også fjerne mellomrom, bruke små bokstaver og bytte ut æøå. [Åpne dette verktøyet](@@tools/app/#convert).

## Find loops {#search}
Søk i gratis kilder etter loops, og last ned og konverter dem i ett steg. Internet Archive, Wikimedia Commons, NASA og Prelinger Archives virker uten konto. Pexels og Pixabay har mange ferdige loops, men trenger en gratis nøkkel, som tar et minutt å lage. Nøkkelen lagres bare i nettleseren din og sendes bare til den siden.
- Opphavsperson og lisens for hver nedlasting lagres i en fil som heter `credits.csv`. Lisensene varierer per klipp, så sjekk dem før du bruker et klipp offentlig.
- Noen sider lar ikke en nettside laste ned filene sine. Bruk da [[Open page]], last ned klippet selv og slipp det i [[Convert]].
- Last bare ned det du har rett til å bruke.

[Åpne dette verktøyet](@@tools/app/#search).

## Filters {#filters}
Legger VJ-aktige looks på en hel mappe med loops: glød, glitch, speil, kaleidoskop, VHS, duotone, pikselering, spor og flere. Trykk [[Preview on first clip]] for å se hver look før du bruker dem. Hver fil får ett nytt klipp per look du velger. [Åpne dette verktøyet](@@tools/app/#filters).

## Crop & trim {#crop}
Beskjærer klipp til bredformat, stående eller kvadrat, og trimmer start og slutt, for en hel mappe på en gang. Velg hvordan det skal passe: beskjær til nøyaktig rammen, eller legg på sorte felt. [Åpne dette verktøyet](@@tools/app/#crop).

## Sizes {#sizes}
Lager en liten proxy, 720p, 1080p og 4K av hvert klipp på en gang. Størrelser som er større enn originalen hoppes over. [Åpne dette verktøyet](@@tools/app/#sizes).

## HAP / ProRes {#pro}
Lager profesjonelle formater for Resolume, VDMX, Millumin og videoredigering. Dette krever den lokale [Linux-versjonen](@guides/offline-linux/#linux), fordi den bruker ffmpeg på din egen datamaskin. [Åpne dette verktøyet](@@tools/app/#pro).

## Catalogue {#catalog}
Lager en nettside og en regnearkfil med bilde, lengde, størrelse og loop-kvalitet for hver loop. Praktisk for store samlinger. [Åpne dette verktøyet](@@tools/app/#catalog).

## Loop pack {#pack}
Pakker loops i en zip du kan dele, med forhåndsbilde, en infofil og en lisens. [Åpne dette verktøyet](@@tools/app/#pack).

## Greit å vite {#know}
- Loops har vanligvis ikke lyd. [[Keep sound]] er av som standard.
- Korte loops gir jevn skrubbing og looping i VJ-programvare.
- Hvis noe feiler, viser jobben årsaken. Se [Hjelp og feilsøking](@guides/help/).

=== queue
name: Kø
title: Kø: følg alle jobbene dine på ett sted
desc: Kø-siden viser alle jobber fra verktøyene og de magiske videomikserne i én liste, så du kan følge lange eksporter og laste ned resultatene.
summary: Alle jobber fra verktøy og miksere i én liste.

## Hva køen er {#what}
Hver lang oppgave, som å konvertere 200 filer eller eksportere en video på 10 minutter, blir en jobb. Kø-siden viser alle jobbene fra verktøyene og begge de magiske videomikserne på ett sted, med status: venter, kjører, ferdig eller feilet.

## Slik bruker du den {#use}
1. Start jobber i et verktøy eller i Magisk videomikser.
2. Åpne [Kø](@@queue/) fra menyen øverst. Et lite tall ved siden av «Kø» viser hvor mange jobber som kjører akkurat nå.
3. Last ned ferdige filer fra listen når de er klare.
4. Trykk [[Clear finished]] for å rydde.

> Jobbene kjører i siden som startet dem. **Ha den siden åpen** til det står ferdig. Kø-siden er et vindu inn til jobbene, den kjører dem ikke.

## Hvor blir filene av? {#files}
Ferdige filer fra verktøyene lagres i denne nettleseren, opptil ca. 600 MB per jobb, så du kan laste dem ned senere. Magisk videomikser beholder sine egne videoer på sin egen side, så bruk [[Open page]] fra køen for å laste ned dem. Ingenting forlater datamaskinen din.

Hvis en fil ikke lenger er lagret, sier køen fra om det, og du kan kjøre jobben på nytt.

=== show-check
name: Klar for showet?
title: Klar for showet? Sjekk enheten din før du går live
desc: En sjekk på ett minutt av datamaskinen og nettleseren før et arrangement: videoformat, ekstra skjerm, lyd, batteri, hastighet og mer.
summary: En sjekk på ett minutt av enheten din før du går live.

## Hva det er {#what}
Inne i Video DJ, VJ-mikseren og mobilversjonene finner du [[Ready for the show?]]. Den sjekker enheten og nettleseren din på et minutt og sier hva som bør fikses før publikum kommer. Ingenting sendes noe sted.

## Slik bruker du den {#use}
1. Åpne mikseren på datamaskinen du skal bruke på arrangementet, med projektoren tilkoblet.
2. Åpne [[Ready for the show?]] og les listen. Hver linje er [[OK]], **Sjekk**, [[Problem]] eller [[Info]].
3. Fiks det som må fikses, og trykk [[Run the check again]].
4. Trykk [[Show test card]] for å se at bildet passer til projektoren.

## Hva hver linje betyr {#lines}
- [[Video format]]. Om nettleseren spiller av mp4 (H.264), som mikserne liker best. Hvis ikke, bruk Chrome, Edge eller Safari, eller konverter videoene med [Verktøy](@guides/tools/).
- [[Works without internet]]. Om siden er lagret for bruk uten nett. Se [Uten internett og Linux](@guides/offline-linux/).
- [[Screen stays awake]]. Om nettleseren kan hindre at skjermen går i hvile. Hvis ikke, slå av skjermspareren og dvalemodus i systeminnstillingene.
- [[Pop-up windows]]. Utgangsvinduet er et popup-vindu. Hvis nettleseren blokkerer popup-vinduer, kan ikke utgangsvinduet åpnes.
- [[Second screen]]. Om en ekstra skjerm er funnet. Koble til projektoren først.
- [[Full screen]] og [[MIDI controller]]. Om de er tilgjengelige, og om en kontroller er tilkoblet.
- [[Sound]]. Om lyden er klar.
- [[Battery]]. Advarer hvis batteriet er lavt. Koble til strøm før showet.
- [[Speed]]. En kort test av hvor mange bilder per sekund skjermen klarer å tegne. Er den treg, lukk andre faner og programmer og bruk mindre bildestørrelse.
- [[Free space]]. Advarer når det er lite diskplass til opptak.
- [[Output window]], loops og spor. Om utgangsvinduet er åpent og om noe er lastet inn.

## Testbildet {#card}
[[Show test card]] åpner et bilde laget for projektorer. Ser du en rund sirkel, alle fire hjørner og den rosa rammen, passer bildet til skjermen. Trykk {{F}} for fullskjerm og {{Esc}} eller klikk for å lukke.

## Be om hjelp med en rapport {#report}
[[Copy report]] kopierer et kort sammendrag av enheten din som ren tekst. Lim det inn i en melding når du ber om hjelp med **Tilbakemelding**-knappen, se [Hjelp](@guides/help/#feedback).

=== offline-linux
name: Uten internett og Linux
title: Bruk Spektronautilus uten internett, installer det og kjør det på Linux
desc: Slik får du siden til å virke uten internett på spillestedet, installerer den som en app, og kjører hele siden lokalt på Linux for mer fart og stabilitet.
summary: Jobb uten internett, installer siden som en app, eller kjør den lokalt på Linux.

## Jobb uten internett {#offline}
Spektronautilus lagrer seg selv i nettleseren din, så det virker også uten Wi-Fi på spillestedet.
1. Åpne siden én gang mens du er på nett.
2. Vent et minutt. Sidene og mikserne lagres.
3. Kjør [Klar for showet?](@guides/show-check/) og sjekk linjen [[Works without internet]].

Du kan også **installere** siden som en app: bruk «Installer» eller «Legg til på hjemskjermen» i nettlesermenyen. Da åpnes den i et eget vindu.

> Verktøyene laster videomotoren sin (ca. 30 MB) første gang du bruker dem. Bruk hvert verktøy én gang mens du er på nett. Linux-versjonen trenger ikke denne motoren.

## Oppdateringer {#updates}
Når en ny versjon er klar, sier en liten linje [[A new version is ready.]] med knappene [[Update now]] og «Senere». Den oppdaterer aldri av seg selv mens siden er åpen, så et pågående show blir aldri forstyrret. Oppdater før arrangementet, ikke under.

## Linux-versjon {#linux}
Det finnes en versjon som kjører hele siden på din egen Linux-maskin. Den kan bare nås fra din egen datamaskin (adresse 127.0.0.1), og den åpnes i Chrome eller Chromium i et eget vindu, startet med innstillinger laget for live visuals.

Hvorfor bruke den:
- **Fart.** Hvis `ffmpeg` er installert, bruker verktøyene den i stedet for den tregere nettlesermotoren. Siden viser da «Fast mode».
- **Ingen minnegrense** for store filer, og du trenger ikke internett (bare [[Find loops]] trenger det).
- **HAP og ProRes.** [HAP / ProRes-verktøyet](@guides/tools/#pro) virker i Linux-versjonen.

Slik installerer du:
1. Last ned Linux-pakken (`spektronautilus-linux.tar.gz`) og pakk den ut: `tar xzf spektronautilus-linux.tar.gz`.
2. Gå inn i mappen og kjør `./install.sh`. Det trenger ikke root-rettigheter. Den legger til en menyoppføring og en `spektronautilus`-kommando, med snarveier til Video DJ, VJ-mikser og loop-verktøyene.
3. For å prøve uten å installere kjører du `./spektronautilus.py` i den utpakkede mappen.
4. `./uninstall.sh` fjerner det igjen.

Du trenger Python 3.8 eller nyere og, for mikserne, Chrome eller Chromium. For å få ffmpeg på Debian eller Ubuntu kjører du `sudo apt install ffmpeg`.

## Trygt fra grunnen av {#safe}
Den lokale serveren godtar bare forespørsler fra din egen datamaskin, avviser andre nettstedsnavn, og lar bare ffmpeg røre sin egen midlertidige mappe, som slettes når du lukker den.

=== help
name: Hjelp og feilsøking
title: Hjelp og feilsøking: når noe ikke virker
desc: Svar på vanlige problemer: videoer som ikke spilles, utgangsvinduet, hakking, en mobil som laster på nytt, MIDI, tapte filer og hvordan du tar kontakt.
summary: Svar på vanlige problemer, og hvordan du tar kontakt.

## En video spilles ikke {#play}
Nesten alltid et formatproblem. Mikserne liker **mp4 med H.264**. Konverter filen med [[Convert]] i [Verktøy](@guides/tools/). iPhone-videoer i HEVC, noen mov-filer og webm-filer kan være et problem i noen nettlesere.

## Jeg får ikke lyd {#sound}
- Loops i VJ-mikseren spilles uten lyd med vilje.
- I Video DJ sjekker du volumet på dekket, masteren og [[Sound follows the crossfader]].
- Nettleseren kan trenge et klikk på siden før den spiller lyd. Klikk én gang på siden.
- Sjekk [[Sound output]] hvis du bruker mer enn én lydenhet.

## Utgangsvinduet åpnes ikke {#output}
Nettleseren blokkerte popup-vinduet. Tillat popup-vinduer for siden og prøv igjen. Sjekken [Klar for showet?](@guides/show-check/) tester dette.

## Bildet hakker {#stutter}
- Velg en mindre bildestørrelse (utgangsstørrelsen) og bruk loops i 720p.
- Lukk andre faner og programmer.
- Bruk en nyere Chrome eller Edge, og koble datamaskinen til strøm.
- Kjør hastighetstesten i [Klar for showet?](@guides/show-check/).
- På en laptop: pass på at nettleseren bruker det kraftige skjermkortet.

## Mobilen laster siden på nytt {#phone}
Telefonen gikk tom for minne, eller skjermen låste seg. Bruk mindre størrelse, 30 eller 24 bilder per sekund, færre eller kortere loops, og hold skjermen på. På iPhone slår du av Lavstrømmodus. I Magisk videomikser slår du av [[Smarter matching (AI)]].

## Eksporten stoppet eller går veldig tregt {#export}
Eksporter går i sanntid, så et spor på 10 minutter trenger omtrent 10 minutter. Ha fanen åpen og synlig, og ikke la datamaskinen gå i dvale. Hvis den ble avbrutt, tilbyr Magisk videomikser å berge det som ble lagret.

## MIDI finner ikke kontrolleren min {#midi}
Bruk Chrome eller Edge på en datamaskin. Koble til kontrolleren først, trykk så [[Enable MIDI]] og tillat det i nettleseren. Andre programmer som bruker kontrolleren kan blokkere den, så lukk dem.

## Hvor er filene mine? {#files}
I nettleseren din, på datamaskinen din. Ferdige resultater fra verktøyene og videoer fra Magisk videomikser står på [Kø](@guides/queue/)-siden. Hvis du sletter nettstedsdata i nettleseren, er de borte, så last ned det du vil beholde.

## Personvern {#privacy}
Ingen kontoer og ingen sporing. Videoer og musikk behandles på enheten din. Når du søker etter loops, kontaktes videokildene du velger, og valgfri Vimeo-opplasting kontakter Vimeo.

## Ta kontakt {#feedback}
Trykk på **Tilbakemelding**-knappen nederst på alle sider og skriv hva som skjedde. Den åpner e-postprogrammet ditt med meldingen ferdig utfylt. Skriv hvilken nettleser du bruker og hva du holdt på med. Ved et problem på en show-datamaskin legger du ved rapporten fra [Klar for showet?](@guides/show-check/#report). Du kan også skrive til oss på [GitHub](https://github.com/munkenbissniss/spektronautilus/issues).
