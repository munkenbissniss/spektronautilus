=== start
name: Empieza aquí
title: Empieza aquí: ¿qué herramienta es la tuya?
desc: Un resumen de dos minutos de Spektronautilus: qué hace cada herramienta, cuál elegir y qué conviene saber antes de empezar.
summary: Un resumen de dos minutos y ayuda para elegir herramienta.

## Qué es Spektronautilus {#what}
Spektronautilus es un conjunto de herramientas gratuitas para VJs, artistas visuales y amantes de la música. Todo funciona en tu navegador. Tus videos y tu música se quedan en tu dispositivo y nunca se suben a ningún sitio.

## ¿Qué herramienta necesito? {#which}
- Tienes **una canción y algunos loops de video** y quieres un video terminado: [Mezclador mágico de video](@guides/magic-mixer/).
- Quieres **poner videoclips en una fiesta o evento**, mezclando dos videos como un DJ: [Video DJ](@guides/video-dj/).
- Quieres **tocar loops en vivo** con pads, capas y efectos al ritmo: [Mezclador VJ](@guides/vj-mixer/).
- Tus loops tienen el **formato equivocado, son demasiado grandes o no enlazan bien**: [Herramientas](@guides/tools/).
- Has lanzado varios trabajos largos y quieres seguirlos: [Cola](@guides/queue/).

## Lo básico {#basics}
- **Navegador.** Un Chrome o Edge reciente en un ordenador funciona mejor. Los mezcladores también funcionan en otros navegadores modernos, pero algunas funciones (MIDI, elegir el dispositivo de sonido) necesitan Chrome o Edge.
- **Móvil o tableta.** Se te envía automáticamente a una versión más sencilla de cada mezclador. Tiene menos funciones para ir fluida.
- **Formato de video.** Usa mp4 con H.264. Se reproduce en todas partes. Si tienes otros formatos, conviértelos con las [Herramientas](@guides/tools/).
- **Idioma.** La web tiene un selector de idioma arriba a la derecha. Dentro de los mezcladores y las herramientas usa el botón 🌐.
- **Claro u oscuro.** Los mezcladores y las herramientas tienen un botón para cambiar de tema.
- **Avanzado.** Cada herramienta empieza con unas pocas opciones sencillas. Los ajustes técnicos están plegados bajo [[Advanced]]. Puedes ignorarlos hasta que los necesites.

## Antes de tu primer show {#show}
Pasa la comprobación [¿Listo para el show?](@guides/show-check/) en el ordenador que vas a usar. En un minuto te dice si el formato de video, la segunda pantalla, el sonido y la velocidad están en orden. Después lee cómo hacer que la web [funcione sin internet](@guides/offline-linux/).

> Prueba las herramientas y ten un plan B preparado. Las herramientas son nuevas, así que prueba todo en casa antes.

## ¿Atascado? {#stuck}
Mira [Ayuda y solución de problemas](@guides/help/). También puedes pulsar el botón **Comentarios** al pie de cada página y contar qué ha pasado.

=== magic-mixer
name: Mezclador mágico de video
title: Mezclador mágico de video: convierte una canción y loops en un video
desc: Añade una canción y tus loops de video. El mezclador escucha la música, encuentra el ritmo y el ambiente, y corta los loops hasta formar un video terminado.
summary: Añade una canción y unos loops y obtén un video terminado que sigue la música.

## Cómo funciona {#how}
Le das al mezclador una pista de música y una carpeta de loops de video. Analiza la música (tempo, ritmo, caídas, partes tranquilas y fuertes) y tus loops (color, brillo, movimiento). Después corta los loops de modo que los cambios caigan en el ritmo y se usen loops parecidos en partes parecidas de la canción.

## Haz tu primer video {#first}
1. **Música.** Suelta un archivo de audio (mp3 funciona mejor) o pulsa [[choose file]]. El mezclador analiza la música y luego muestra el tempo.
2. **Loops de video.** Suelta videos o una carpeta entera. La versión de escritorio admite hasta 100 loops. Los loops que enlazan bien y tienen el mismo tamaño funcionan mejor. Si tus clips no enlazan con suavidad, arréglalos primero con [[Make loops]] en las [Herramientas](@guides/tools/).
3. **Ajustes de la mezcla.** Pulsa [[Recommended]]. El mezclador mira la música y tus loops y propone un ambiente. También puedes elegirlo tú, por ejemplo [[Chill]], [[Ambient]] o [[Groove]]. Después aún puedes cambiar todo.
4. **Exportar.** Pulsa [[Add to export queue]]. El video se crea mientras la página está abierta.

> La exportación va en tiempo real. Una pista de 10 minutos tarda unos 10 minutos. Mantén la pestaña abierta y no esperes sonido mientras trabaja.

## Ajustes que conviene conocer {#settings}
La mayoría de la gente nunca los necesita. Están en las secciones [[Advanced]].
- [[Typical shot length (bars)]] es cuánto tiempo se queda un clip en pantalla, contado en compases. 4 compases es relajado, 8 es lento, 16 a 32 es muy lento y ambiental.
- [[Crossfade length (beats)]] decide con qué suavidad se funde un clip con el siguiente. 0 es un corte seco.
- [[Loops per section]] es cuántos loops comparten una parte de la canción. 2 da un A-B-A-B tranquilo.
- [[Style match]] hace que el siguiente clip se parezca al anterior, para que la mezcla fluya.
- [[Layers & looks]] mezcla un segundo clip por encima, añade un tono de color por sección y deja que la imagen respire con la música.
- [[Motion & effects]] añaden zoom al ritmo, sacudida, pulso de brillo y estelas. Todo es suave por defecto.
- [[Use every loop]] intenta mostrar todos tus loops al menos una vez.
- [[Use CLIP (AI image understanding)]] deja que un modelo de IA (CLIP) mire tus loops. Descarga unos 100 a 150 MB la primera vez, así que usa Wi-Fi. Después funciona sin conexión.
- [[Seed (empty = random)]]. La misma semilla y los mismos ajustes dan la misma mezcla. Usa [[Versions]] para crear varias mezclas distintas a la vez.

## Exportar y compartir {#export}
- **Formato.** MP4 (H.264). Elige el tamaño (960×540, 1280×720 o 1920×1080), la tasa de fotogramas y la calidad. 8 Mbit/s son unos 600 MB por cada 10 minutos.
- **Dónde está el video.** Los videos terminados se quedan dentro de la página hasta que los descargues o los quites. [[Storage in this browser]] muestra cuánto espacio ocupan y [[Delete all stored videos]] lo vacía.
- [[Upload to Vimeo (optional)]]. Pega tu propio token de acceso de Vimeo. Solo se guarda en tu navegador y solo se envía a Vimeo. Los videos son privados por defecto.
- **Sigue los trabajos** en la página de la [Cola](@guides/queue/).

## La versión para móvil {#phone}
La versión para móvil está hecha para el teléfono. Elige una pista y unos videos, escoge un ambiente y una forma (horizontal o vertical) y pulsa [[Make video]].
- Mantén la página abierta y la pantalla encendida mientras se crea el video. En un iPhone, desactiva primero el modo de bajo consumo, porque detiene la reproducción de video.
- Si el teléfono va justo o la página se recarga, elige 30 o 24 fotogramas por segundo, un tamaño menor, menos loops o una pista más corta.
- La coincidencia con IA pesa mucho en un teléfono. Desactívala si la página se recarga sola.
- Si algo se interrumpe, la página ofrece descargar lo guardado ([[Download recovered video]]).

## Consejos {#tips}
- Usa loops con el mismo tamaño y los mismos fotogramas por segundo. Los tamaños mezclados funcionan, pero es más tranquilo si coinciden.
- Empieza con 720p. Sube solo cuando lo necesites.
- ¿No te convence? Pulsa [[Recommended]] otra vez, cambia el ambiente o usa otra semilla.
- ¿Algo falla? Mira [Ayuda y solución de problemas](@guides/help/).

=== video-dj
name: Video DJ
title: Video DJ: mezcla videoclips en dos platos
desc: Mezcla videoclips completos como un DJ, con dos platos, crossfader, vista previa, logotipo, carteles de texto, MIDI y una ventana de salida limpia para tu proyector.
summary: Mezcla videoclips en dos platos con crossfader, pensado para eventos.

## Qué es {#what}
Video DJ tiene dos platos para videoclips (mp4, mov, webm). Imagen y sonido se mezclan juntos. Ves una vista previa de ambos platos junto a la salida, y una ventana de salida aparte va al proyector o a la tele.

> La herramienta está pensada para un ordenador con Chrome o Edge. En el móvil obtienes una versión más sencilla con dos platos, crossfader, efectos, carteles y una forma de enviar la imagen a otra pantalla.

## Tu primera mezcla {#first}
1. **Añade videos.** Suelta videoclips en la página o pulsa [[Add files…]]. Nombres como «Artista - Título.mp4» se convierten en texto del cartel. Suelta un video directamente sobre un plato para cargarlo al instante.
2. **Carga los platos.** Pon un video en el plato A y otro en el B. Pulsa play en cada uno.
3. **Abre la ventana de salida.** Pulsa [[Open output window]], arrastra la ventana nueva al proyector y pulsa {{F}} para pantalla completa. Mantén abierta la ventana de control durante el show.
4. **Mezcla.** Mueve el crossfader a mano o pulsa [[Mix to other deck (auto fade)]] para un fundido suave. [[Fade time]] decide cuánto dura.

## Auto-mix {#automix}
Activa [[Auto-mix to the next track]] y el mezclador empieza la siguiente pista en el plato libre por ti, unos segundos antes de que acabe la actual. Tú decides cuántos. Úsalo en sets largos o cuando necesites un descanso.

## Sonido {#sound}
- [[Sound follows the crossfader]] funde el sonido junto con la imagen.
- [[Smooth (equal power)]] o [[Linear]] decide la curva del fundido de sonido.
- Un limitador suave en la mezcla maestra evita que dos pistas fuertes saturen al solaparse.
- [[Sound output]] te deja elegir otro dispositivo de sonido (Chrome o Edge).

## Logotipo y carteles {#posters}
- **Logotipo.** Añade un PNG con transparencia (funciona mejor). El logotipo queda en la esquina superior derecha de la imagen. Elige su tamaño y actívalo o desactívalo con un botón.
- **Carteles.** Un cartel es un texto que se desliza, con una línea grande y otra pequeña. Elige un color predefinido, desde dónde entra y cuánto se queda. Guarda carteles en ranuras y muéstralos con un clic o una tecla.
- **Nombre de la pista.** Activa [[Show the track name when a track mixes in]] y el cartel aparece solo.

## Controlador MIDI {#midi}
Conecta tu controlador, pulsa [[Enable MIDI]] (Chrome o Edge en ordenador), pulsa [[Learn]] junto a una función y mueve el control que quieras usar.

## Grabar y retransmitir {#record}
- [[● Record]] guarda la mezcla, imagen y sonido, en un archivo.
- Para retransmitir, captura la ventana de salida en OBS (Window Capture) o usa «Cast…» de Chrome y elige la ventana de salida. El mezclador no envía video por internet por sí mismo.

## Hecho para no fallar {#safe}
- Las pistas se cargan enteras en la memoria antes de reproducirse (los archivos de más de 1,5 GB se leen en directo), así que el disco no puede interrumpir una pista.
- Un problema con un archivo muestra un mensaje y nunca detiene el otro plato.
- La imagen sigue funcionando con la ventana de control en segundo plano, y si cierras la ventana por error, te lo pregunta antes.
- Pasa la comprobación [¿Listo para el show?](@guides/show-check/) antes de cada evento.

## La versión para móvil {#phone}
Dos platos, crossfader, efectos (Zoom, Flash, Strobe, Invert, Mirror), carteles y pantalla completa. Para mostrar la imagen en otra pantalla, abre [[Send to another screen]]: crea un código, abre el enlace en la otra pantalla (un portátil, el navegador de una tele o un ordenador de proyector en la misma Wi-Fi) y pega el código de respuesta. Nada pasa por un servidor.

> Los efectos intermitentes pueden provocar crisis en algunas personas. Mantenlos lentos en eventos públicos.

=== vj-mixer
name: Mezclador VJ
title: Mezclador VJ: toca loops en vivo con pads y capas
desc: Toca tus loops en vivo. Dos canales con tres capas cada uno, 20 pads de loops, crossfader y efectos que siguen el tempo.
summary: Toca loops en vivo en 20 pads con capas, crossfader y efectos al ritmo.

## Qué es {#what}
El Mezclador VJ sirve para tocar loops de video cortos en vivo. Tienes 20 pads, dos canales (A y B) con tres capas cada uno, un crossfader y efectos sencillos que siguen el ritmo. Los loops se reproducen sin sonido.

> Está pensado para un ordenador con Chrome o Edge. En el móvil obtienes una versión más pequeña con 8 pads y 2 capas por canal.

## Llena los pads {#pads}
Suelta archivos de loops sobre la cuadrícula de pads o pulsa [[Add loops…]]. Llenan los pads vacíos. Usa loops mp4 (H.264) para la reproducción más fluida. Para reutilizarlos la próxima vez, activa [[Remember my loops on this computer]]. Se guardan solo en este navegador.

## Toca {#play}
1. **Elige una capa.** Cada canal tiene tres capas. Selecciona la capa en la que quieres tocar.
2. **Pulsa un pad** (o su tecla en el teclado). El loop empieza al instante en la capa seleccionada.
3. **Mezcla las capas.** Cada capa tiene su propia opacidad y un modo de mezcla: normal, add, screen o multiply.
4. **Mezcla los canales.** Usa el crossfader o [[Mix to other channel (auto fade)]]. [[Clear layer]] vacía una capa.

## El ritmo {#beat}
Los efectos siguen un ritmo. Puedes fijarlo de tres maneras:
- **Toca** el botón de tempo varias veces o escribe los **BPM**.
- Deja que el mezclador **escuche el bombo** a través de una entrada de audio ([[Audio input (kick drum)]]). Ajusta con [[Sensitivity]].
- Pulsa [[Set beat 1 (downbeat)]] en el momento que deba contar como el primer tiempo de un compás.

## Efectos al ritmo {#effects}
Zoom, Shake, Flash, Strobe, Invert, Mirror, Colour spin y Blur. Activa cada uno, elige con qué frecuencia pulsa (cada tiempo, 2 tiempos o 4 tiempos) y con qué fuerza.

> Flash, Strobe e Invert a tempo rápido pueden provocar crisis en algunas personas. Mantenlo lento en eventos públicos.

## Logotipo, carteles, MIDI y salida {#more}
Funcionan como en [Video DJ](@guides/video-dj/#posters): un logotipo, carteles de texto que se deslizan, control MIDI con [[Learn]] y una ventana de salida para el proyector (pulsa {{F}} para pantalla completa). Para retransmitir, captura la ventana de salida en OBS o usa «Cast…» de Chrome.

## La versión para móvil {#phone}
8 pads, dos capas por canal, crossfader y efectos, con las mismas herramientas de ritmo. Aquí los loops también se reproducen sin sonido.

## ¿Loops demasiado pesados? {#heavy}
Usa mp4 (H.264) en 720p o 1080p. Convierte otros formatos y reduce los archivos grandes con las [Herramientas](@guides/tools/). Pasa la comprobación [¿Listo para el show?](@guides/show-check/) para ver lo fluido que va tu ordenador.

=== tools
name: Herramientas de loops
title: Herramientas de loops: convierte, arregla, filtra y organiza tus loops
desc: Herramientas gratuitas en el navegador para loops de VJ: convierte GIF y video, crea loops perfectos, recorta, cambia el tamaño, añade looks, encuentra loops gratis y crea paquetes.
summary: Convierte, enlaza, recorta, filtra, busca y empaqueta tus loops de video.

## Cómo funcionan las herramientas {#how}
Abre las herramientas y elige una de la lista. Todas siguen el mismo patrón:
1. **Añade archivos.** Suelta archivos o una carpeta, o pulsa [[choose files]].
2. **Ajustes.** Unas pocas opciones sencillas. Los ajustes técnicos están bajo [[Advanced]].
3. **Empieza.** El trabajo se convierte en tareas de una lista. Puedes poner muchos archivos en cola y dejar que siga. Mira la [Cola](@guides/queue/).
4. **Descarga.** Los resultados son archivos mp4 normales que puedes usar en cualquier programa de VJ.

Todo funciona dentro de tu navegador y tus archivos nunca salen de tu ordenador. Los archivos grandes no son un problema, se leen directamente del disco. En Chrome o Edge también puedes elegir una carpeta y guardar cada resultado directamente en ella ([[Save each file straight into a folder I choose]]).

> La versión del navegador es más lenta que un programa de escritorio (unas 5 a 10 veces). Para muchos archivos 4K grandes usa la [versión para Linux](@guides/offline-linux/#linux), que usa el motor rápido de tu propio ordenador.

## GIF to MP4 {#gif2mp4}
Convierte muchos GIF a mp4 fluido de una vez, también GIF con transparencia. Para GIF transparentes, elige un color de fondo (negro, blanco o #rrggbb). [[Keep shape, only shrink]] mantiene pequeños los GIF pequeños. [Abrir esta herramienta](@@tools/app/#gif2mp4).

## Make loops {#loop}
Comprueba si un clip ya enlaza como loop. Si es así, lo deja como está. Si no, puede recortarlo hasta el mejor punto de enlace, reproducirlo hacia delante y luego hacia atrás, o fundir el final con el principio. [[Auto: keep good loops, otherwise fix them]] elige por ti: conserva los buenos loops y arregla los demás. También puedes fijar una duración mínima, porque al Mezclador mágico le gustan los loops de 16 segundos o más. [Abrir esta herramienta](@@tools/app/#loop).

## Convert {#convert}
Convierte mov, webm, mkv, gif y otros formatos en mp4 adecuado para VJ. Elige tamaño, fotogramas por segundo y calidad, y usa una [[Name template]] para renombrar en bloque. La plantilla entiende códigos como `{name}`, `{n}`, `{n2}` (un número de dos cifras), `{w}`, `{h}`, `{res}`, `{fps}`, `{dur}` y `{date}`. También puedes quitar espacios, pasar a minúsculas y sustituir æøå. [Abrir esta herramienta](@@tools/app/#convert).

## Find loops {#search}
Busca loops en fuentes gratuitas, y descárgalos y conviértelos de una vez. Internet Archive, Wikimedia Commons, NASA y los Prelinger Archives funcionan sin cuenta. Pexels y Pixabay tienen muchos loops ya hechos, pero necesitan una clave gratuita, que se consigue en un minuto. La clave se guarda solo en tu navegador y solo se envía a ese sitio.
- El autor y la licencia de cada descarga se guardan en un archivo llamado `credits.csv`. Las licencias varían según el clip, así que compruébalas antes de usar un clip en público.
- Algunos sitios no permiten que una página web descargue sus archivos. Entonces usa [[Open page]], descarga el clip tú mismo y suéltalo en [[Convert]].
- Descarga solo lo que tengas derecho a usar.

[Abrir esta herramienta](@@tools/app/#search).

## Filters {#filters}
Añade looks de estilo VJ a una carpeta entera de loops: brillo, glitch, espejo, caleidoscopio, VHS, duotono, pixelado, estelas y más. Pulsa [[Preview on first clip]] para ver cada look antes de aplicarlos. Cada archivo recibe un clip nuevo por cada look que elijas. [Abrir esta herramienta](@@tools/app/#filters).

## Crop & trim {#crop}
Recorta clips a formato panorámico, vertical o cuadrado, y recorta el principio y el final, para una carpeta entera de una vez. Elige cómo encajar: recortar al marco exacto o añadir barras negras. [Abrir esta herramienta](@@tools/app/#crop).

## Sizes {#sizes}
Crea un proxy pequeño, 720p, 1080p y 4K de cada clip de una vez. Los tamaños mayores que el original se omiten. [Abrir esta herramienta](@@tools/app/#sizes).

## HAP / ProRes {#pro}
Crea formatos profesionales para Resolume, VDMX, Millumin y editores de video. Necesita la [versión local para Linux](@guides/offline-linux/#linux), porque usa ffmpeg en tu propio ordenador. [Abrir esta herramienta](@@tools/app/#pro).

## Escalado con IA {#ai}
Hace los clips de video más nítidos y grandes con IA, usando el programa gratuito Video2X. Solo funciona en la [versión local para Linux](@guides/offline-linux/#linux) y necesita una tarjeta gráfica compatible con Vulkan. Tus archivos nunca salen de tu ordenador.

Cómo usarlo:
1. Instala Video2X tú mismo (un AppImage, el paquete del AUR o tu propia compilación). Spektronautilus lo encuentra solo. Si no, indica la ruta en la variable `SPEKTRO_VIDEO2X` y vuelve a iniciar Spektronautilus.
2. Abre la herramienta y añade tus clips. La nota sobre los ajustes indica si se encontró Video2X.
3. Elige [[Kind of picture]] y [[Make it this much bigger]], y pulsa [[Upscale]].

Conviene saber:
- Es lento. Un clip corto puede tardar muchos minutos, así que usa la [cola](@guides/queue/) y déjalo trabajar.
- Las fotos y la película real siempre se agrandan 4×. El resultado no puede superar 8K.
- ¿Tienes más de una tarjeta gráfica? Pulsa [[Check my graphics card]] y ajusta [[Graphics card number]].

## Catalogue {#catalog}
Crea una página web y un archivo de hoja de cálculo con una imagen, la duración, el tamaño y la calidad de enlace de cada loop. Útil para colecciones grandes. [Abrir esta herramienta](@@tools/app/#catalog).

## Loop pack {#pack}
Reúne loops en un zip que puedes compartir, con imagen de vista previa, un archivo de información y una licencia. [Abrir esta herramienta](@@tools/app/#pack).

## Conviene saber {#know}
- Los loops normalmente no llevan sonido. [[Keep sound]] está desactivado por defecto.
- Los loops cortos dan un desplazamiento y un bucle fluidos en el software de VJ.
- Si algo falla, la tarea muestra el motivo. Mira [Ayuda y solución de problemas](@guides/help/).

=== queue
name: Cola
title: Cola: sigue todos tus trabajos en un solo lugar
desc: La página Cola muestra en una lista todos los trabajos de las herramientas y de los mezcladores mágicos de video, para que sigas las exportaciones largas y descargues los resultados.
summary: Todos los trabajos de las herramientas y los mezcladores en una lista.

## Qué es la Cola {#what}
Cada tarea larga, como convertir 200 archivos o exportar un video de 10 minutos, se convierte en un trabajo. La página Cola muestra todos los trabajos de las herramientas y de ambos mezcladores mágicos en un solo lugar, con su estado: esperando, en marcha, terminado o fallido.

## Cómo usarla {#use}
1. Inicia trabajos en una herramienta o en el Mezclador mágico de video.
2. Abre la [Cola](@@queue/) desde el menú superior. Un pequeño número junto a «Cola» indica cuántos trabajos están en marcha ahora mismo.
3. Descarga los archivos terminados de la lista cuando estén listos.
4. Pulsa [[Clear finished]] para ordenar.

> Los trabajos se ejecutan en la página que los inició. **Mantén esa página abierta** hasta que diga que ha terminado. La página Cola es una ventana a los trabajos, no los ejecuta.

## ¿Dónde acaban los archivos? {#files}
Los archivos terminados de las herramientas se guardan en este navegador, hasta unos 600 MB por trabajo, para que puedas descargarlos más tarde. El Mezclador mágico guarda sus propios videos en su propia página, así que usa [[Open page]] desde la Cola para descargarlos. Nada sale de tu ordenador.

Si un archivo ya no está guardado, la Cola lo dice y puedes repetir el trabajo.

=== show-check
name: ¿Listo para el show?
title: ¿Listo para el show? Comprueba tu dispositivo antes de salir en vivo
desc: Una comprobación de un minuto de tu ordenador y tu navegador antes de un evento: formato de video, segunda pantalla, sonido, batería, rendimiento y más.
summary: Una comprobación de un minuto de tu dispositivo antes de salir en vivo.

## Qué es {#what}
Dentro de Video DJ, el Mezclador VJ y sus versiones para móvil encuentras [[Ready for the show?]]. Comprueba tu dispositivo y tu navegador en un minuto y te dice qué arreglar antes de que llegue el público. No se envía nada a ningún sitio.

## Cómo usarla {#use}
1. Abre el mezclador en el ordenador que usarás en el evento, con el proyector conectado.
2. Abre [[Ready for the show?]] y lee la lista. Cada línea es [[OK]], [[Check]], [[Problem]] o [[Info]].
3. Arregla lo que haga falta y pulsa [[Run the check again]].
4. Pulsa [[Show test card]] para ver que la imagen encaja en el proyector.

## Qué significa cada línea {#lines}
- [[Video format]]. Si el navegador reproduce mp4 (H.264), que es lo que mejor les va a los mezcladores. Si no, usa Chrome, Edge o Safari, o convierte tus videos con las [Herramientas](@guides/tools/).
- [[Works without internet]]. Si la web está guardada para usarla sin conexión. Mira [Sin internet y Linux](@guides/offline-linux/).
- [[Screen stays awake]]. Si el navegador puede evitar que la pantalla se apague. Si no, desactiva el salvapantallas y la suspensión en los ajustes del sistema.
- [[Pop-up windows]]. La ventana de salida es una ventana emergente. Si el navegador las bloquea, la ventana de salida no se puede abrir.
- [[Second screen]]. Si se encuentra una segunda pantalla. Conecta primero el proyector.
- [[Full screen]] y [[MIDI controller]]. Si están disponibles y si hay un controlador conectado.
- [[Sound]]. Si el sonido está listo.
- [[Battery]]. Avisa si la batería está baja. Enchúfalo antes del show.
- [[Speed]]. Una prueba corta de cuántos fotogramas por segundo puede dibujar la pantalla. Si es lenta, cierra otras pestañas y programas y usa un tamaño de imagen menor.
- [[Free space]]. Avisa cuando hay poco espacio en disco para grabar.
- [[Output window]], loops y pistas. Si la ventana de salida está abierta y si hay algo cargado.

## La carta de ajuste {#card}
[[Show test card]] abre una imagen hecha para proyectores. Si ves un círculo redondo, las cuatro esquinas y el marco rosa, la imagen encaja en la pantalla. Pulsa {{F}} para pantalla completa y {{Esc}} o haz clic para cerrarla.

## Pedir ayuda con un informe {#report}
[[Copy report]] copia un breve resumen de tu dispositivo en texto plano. Pégalo en un mensaje cuando pidas ayuda con el botón **Comentarios**, mira [Ayuda](@guides/help/#feedback).

=== offline-linux
name: Sin internet y Linux
title: Usa Spektronautilus sin internet, instálalo y ejecútalo en Linux
desc: Cómo hacer que la web funcione sin internet en el local, instalarla como una app y ejecutar toda la web en local en Linux para más velocidad y estabilidad.
summary: Trabaja sin internet, instala la web como una app o ejecútala en local en Linux.

## Trabajar sin internet {#offline}
Spektronautilus se guarda en tu navegador, así que también funciona sin Wi-Fi en el local.
1. Abre la web una vez mientras estás conectado.
2. Espera un minuto. Se están guardando las páginas y los mezcladores.
3. Pasa [[Ready for the show?]] y mira la línea [[Works without internet]].

También puedes **instalar** la web como una app: usa «Instalar» o «Añadir a la pantalla de inicio» en el menú del navegador. Se abre entonces en su propia ventana.

> Las herramientas cargan su motor de video (unos 30 MB) la primera vez que las usas. Usa cada herramienta una vez mientras estás conectado. La versión para Linux no necesita ese motor.

## Actualizaciones {#updates}
Cuando hay una versión nueva, una barra pequeña dice [[A new version is ready.]] con los botones [[Update now]] y «Más tarde». Nunca se actualiza sola mientras la página está abierta, así que un show en marcha nunca se interrumpe. Actualiza antes del evento, no durante.

## Versión para Linux {#linux}
Hay una versión que ejecuta toda la web en tu propio ordenador Linux. Solo es accesible desde tu ordenador (dirección 127.0.0.1) y se abre en Chrome o Chromium en su propia ventana, iniciado con ajustes pensados para visuales en vivo.

Por qué usarla:
- **Velocidad.** Si `ffmpeg` está instalado, las herramientas lo usan en lugar del motor más lento del navegador. La página dice entonces «Fast mode».
- **Sin límite de memoria** para archivos grandes, y no hace falta internet (solo [[Find loops]] lo necesita).
- **HAP y ProRes.** La [herramienta HAP / ProRes](@guides/tools/#pro) funciona en la versión para Linux.
- **Escalado con IA.** La [herramienta de escalado con IA](@guides/tools/#ai) usa Video2X, si lo has instalado.

Cómo instalarla:
1. Descarga el paquete para Linux (`spektronautilus-linux.tar.gz`) y descomprímelo: `tar xzf spektronautilus-linux.tar.gz`.
2. Entra en la carpeta y ejecuta `./install.sh`. No necesita permisos de root. Añade una entrada de menú y un comando `spektronautilus`, con accesos directos a Video DJ, el Mezclador VJ y las herramientas de loops.
3. Para probarlo sin instalar, ejecuta `./spektronautilus.py` en la carpeta descomprimida.
4. `./uninstall.sh` lo quita de nuevo.

Necesitas Python 3.8 o superior y, para los mezcladores, Chrome o Chromium. Para tener ffmpeg en Debian o Ubuntu, ejecuta `sudo apt install ffmpeg`.

## Seguro por diseño {#safe}
El servidor local solo acepta peticiones de tu propio ordenador, rechaza otros nombres de sitio web y solo deja que ffmpeg toque su propia carpeta temporal, que se borra al cerrarlo.

=== help
name: Ayuda y solución de problemas
title: Ayuda y solución de problemas: cuando algo no funciona
desc: Respuestas a problemas comunes: videos que no se reproducen, la ventana de salida, tirones, un móvil que se recarga, MIDI, archivos perdidos y cómo contactar.
summary: Respuestas a problemas comunes y cómo ponerse en contacto.

## Un video no se reproduce {#play}
Casi siempre es un problema de formato. A los mezcladores les gusta **mp4 con H.264**. Convierte el archivo con [[Convert]] en las [Herramientas](@guides/tools/). Los videos de iPhone en HEVC, algunos archivos mov y los webm pueden dar problemas en algunos navegadores.

## No hay sonido {#sound}
- Los loops del Mezclador VJ se reproducen sin sonido a propósito.
- En Video DJ, revisa el volumen del plato, el master y [[Sound follows the crossfader]].
- El navegador puede necesitar un clic en la página antes de reproducir sonido. Haz un clic en la página.
- Revisa [[Sound output]] si usas más de un dispositivo de sonido.

## La ventana de salida no se abre {#output}
El navegador bloqueó la ventana emergente. Permite las ventanas emergentes para el sitio y vuelve a intentarlo. La comprobación [¿Listo para el show?](@guides/show-check/) lo prueba.

## La imagen va a tirones {#stutter}
- Elige un tamaño de imagen menor (el tamaño de salida) y usa loops de 720p.
- Cierra otras pestañas y programas.
- Usa un Chrome o Edge reciente y enchufa el ordenador.
- Haz la prueba de velocidad de [¿Listo para el show?](@guides/show-check/).
- En un portátil, asegúrate de que el navegador usa la tarjeta gráfica potente.

## Mi móvil recarga la página {#phone}
El teléfono se quedó sin memoria o se bloqueó la pantalla. Usa un tamaño menor, 30 o 24 fotogramas por segundo, menos loops o más cortos, y mantén la pantalla encendida. En un iPhone, desactiva el modo de bajo consumo. En el Mezclador mágico de video, desactiva la coincidencia con IA.

## La exportación se detuvo o va muy lenta {#export}
Las exportaciones van en tiempo real, así que una pista de 10 minutos necesita unos 10 minutos. Mantén la pestaña abierta y visible, y no dejes que el ordenador se suspenda. Si se interrumpió, el Mezclador mágico de video ofrece recuperar lo guardado.

## MIDI no encuentra mi controlador {#midi}
Usa Chrome o Edge en un ordenador. Conecta primero el controlador, luego pulsa [[Enable MIDI]] y permítelo en el navegador. Otros programas que usen el controlador pueden bloquearlo, así que ciérralos.

## ¿Dónde están mis archivos? {#files}
En tu navegador, en tu ordenador. Los resultados terminados de las herramientas y los videos del Mezclador mágico aparecen en la página [Cola](@guides/queue/). Si borras los datos del sitio en tu navegador, desaparecen, así que descarga lo que quieras conservar.

## Privacidad {#privacy}
Sin cuentas y sin seguimiento. Los videos y la música se procesan en tu dispositivo. Al buscar loops se contacta con las fuentes de video que elijas, y la subida opcional a Vimeo contacta con Vimeo.

## Ponte en contacto {#feedback}
Pulsa el botón **Comentarios**, al pie de cada página, y escribe qué ha pasado. Abre tu programa de correo con el mensaje ya preparado. Añade qué navegador usas y qué estabas haciendo. Si el problema es en el ordenador de un show, añade el informe de [¿Listo para el show?](@guides/show-check/#report). También puedes escribirnos en [GitHub](https://github.com/munkenbissniss/spektronautilus/issues).
