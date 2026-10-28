=== start
name: Comece aqui
title: Comece aqui: que ferramenta é a certa para si?
desc: Uma visão geral de dois minutos do Spektronautilus: o que faz cada ferramenta, qual escolher e o que convém saber antes de começar.
summary: Uma visão geral de dois minutos e ajuda para escolher a ferramenta.

## O que é o Spektronautilus {#what}
O Spektronautilus é um conjunto de ferramentas gratuitas para VJs, artistas visuais e amantes de música. Tudo funciona no seu navegador. Os seus vídeos e a sua música ficam no seu dispositivo e nunca são enviados para lado nenhum.

## De que ferramenta preciso? {#which}
- Tem **uma música e alguns loops de vídeo** e quer um vídeo pronto: [Mixer mágico de vídeo](@guides/magic-mixer/).
- Quer **pôr videoclipes numa festa ou evento**, misturando dois vídeos como um DJ: [Video DJ](@guides/video-dj/).
- Quer **tocar loops ao vivo** com pads, camadas e efeitos ao ritmo: [Mixer VJ](@guides/vj-mixer/).
- Os seus loops têm o **formato errado, são demasiado grandes ou não encaixam bem**: [Ferramentas](@guides/tools/).
- Iniciou vários trabalhos longos e quer acompanhá-los: [Fila](@guides/queue/).

## O essencial {#basics}
- **Navegador.** Um Chrome ou Edge recente num computador funciona melhor. Os mixers também funcionam noutros navegadores modernos, mas algumas funções (MIDI, escolha do dispositivo de som) precisam de Chrome ou Edge.
- **Telemóvel ou tablet.** É enviado automaticamente para uma versão mais simples de cada mixer. Tem menos funções para correr com fluidez.
- **Formato de vídeo.** Use mp4 com H.264. Reproduz em todo o lado. Se tem outros formatos, converta-os com as [Ferramentas](@guides/tools/).
- **Idioma.** O site tem um seletor de idioma no canto superior direito. Dentro dos mixers e das ferramentas use o botão 🌐.
- **Claro ou escuro.** Os mixers e as ferramentas têm um botão para mudar o tema.
- **Avançado.** Cada ferramenta começa com algumas escolhas simples. As definições técnicas ficam recolhidas em [[Advanced]]. Pode ignorá-las até precisar delas.

## Antes do seu primeiro show {#show}
Faça a verificação [Pronto para o show?](@guides/show-check/) no computador que vai usar. Em um minuto diz-lhe se o formato de vídeo, o segundo ecrã, o som e a velocidade estão em ordem. Depois leia como fazer o site [funcionar sem internet](@guides/offline-linux/).

> Teste as ferramentas e tenha um plano B pronto. As ferramentas são novas, por isso experimente tudo primeiro em casa.

## Ficou preso? {#stuck}
Veja [Ajuda e resolução de problemas](@guides/help/). Pode também carregar no botão **Comentários** no fim de cada página e contar o que aconteceu.

=== magic-mixer
name: Mixer mágico de vídeo
title: Mixer mágico de vídeo: transforme uma música e loops num vídeo
desc: Adicione uma música e os seus loops de vídeo. O mixer ouve a música, encontra o ritmo e o ambiente e corta os loops num vídeo pronto.
summary: Adicione uma música e uns loops e obtenha um vídeo pronto que segue a música.

## Como funciona {#how}
Dá ao mixer uma faixa de música e uma pasta com loops de vídeo. Ele analisa a música (tempo, ritmo, quebras, partes calmas e fortes) e os seus loops (cor, brilho, movimento). Depois corta os loops de modo a que as mudanças caiam no ritmo e se usem loops parecidos em partes parecidas da música.

## Faça o seu primeiro vídeo {#first}
1. **Música.** Largue um ficheiro de áudio (mp3 funciona melhor) ou carregue em [[choose file]]. O mixer analisa a música e depois mostra o tempo.
2. **Loops de vídeo.** Largue vídeos ou uma pasta inteira. A versão de computador aceita até 100 loops. Loops que encaixam bem e têm o mesmo tamanho funcionam melhor. Se os seus clipes não encaixam com suavidade, corrija-os primeiro com [[Make loops]] nas [Ferramentas](@guides/tools/).
3. **Definições da mistura.** Carregue em [[Recommended]]. O mixer olha para a música e para os loops e sugere um ambiente. Também pode escolher o ambiente, por exemplo [[Chill]], [[Ambient]] ou [[Groove]]. Depois ainda pode mudar tudo.
4. **Exportar.** Carregue em [[Add to export queue]]. O vídeo é criado enquanto a página está aberta.

> A exportação corre em tempo real. Uma faixa de 10 minutos demora cerca de 10 minutos. Mantenha o separador aberto e não espere som enquanto trabalha.

## Definições que convém conhecer {#settings}
A maioria das pessoas nunca precisa delas. Estão nas secções [[Advanced]].
- [[Typical shot length (bars)]] é quanto tempo um clipe fica no ecrã, contado em compassos. 4 compassos é descontraído, 8 é lento, 16 a 32 é muito lento e ambiente.
- [[Crossfade length (beats)]] decide com que suavidade um clipe se funde no seguinte. 0 é um corte seco.
- [[Loops per section]] é quantos loops partilham uma parte da música. 2 dá um A-B-A-B calmo.
- [[Style match]] faz com que o clipe seguinte se pareça com o anterior, para a mistura fluir.
- [[Layers & looks]] mistura um segundo clipe por cima, dá um tom de cor a cada secção e deixa a imagem respirar com a música.
- [[Motion & effects]] acrescentam zoom ao ritmo, abanão, pulso de brilho e rastos. Tudo é suave por predefinição.
- [[Use every loop]] tenta mostrar todos os seus loops pelo menos uma vez.
- [[Use CLIP (AI image understanding)]] deixa um modelo de IA (CLIP) olhar para os seus loops. Descarrega cerca de 100 a 150 MB à primeira vez, por isso use Wi-Fi. Depois funciona sem ligação.
- [[Seed (empty = random)]]. A mesma semente e as mesmas definições dão a mesma mistura. Use [[Versions]] para criar várias misturas diferentes de uma vez.

## Exportar e partilhar {#export}
- **Formato.** MP4 (H.264). Escolha o tamanho (960×540, 1280×720 ou 1920×1080), a taxa de fotogramas e a qualidade. 8 Mbit/s são cerca de 600 MB por cada 10 minutos.
- **Onde está o vídeo.** Os vídeos prontos ficam dentro da página até os descarregar ou remover. [[Storage in this browser]] mostra quanto espaço ocupam e [[Delete all stored videos]] esvazia-o.
- [[Upload to Vimeo (optional)]]. Cole o seu próprio token de acesso do Vimeo. Fica guardado só no seu navegador e é enviado só para o Vimeo. Os vídeos são privados por predefinição.
- **Acompanhe os trabalhos** na página da [Fila](@guides/queue/).

## A versão para telemóvel {#phone}
A versão para telemóvel é feita para o telefone. Escolha uma faixa e uns vídeos, um ambiente e uma forma (horizontal ou vertical) e carregue em [[Make video]].
- Mantenha a página aberta e o ecrã ligado enquanto o vídeo é criado. No iPhone, desligue primeiro o modo de poupança de energia, porque pára a reprodução de vídeo.
- Se o telefone tiver dificuldades ou a página recarregar, escolha 30 ou 24 fotogramas por segundo, um tamanho menor, menos loops ou uma faixa mais curta.
- A correspondência inteligente com IA é pesada para um telefone. Desligue-a se a página recarregar sozinha.
- Se algo for interrompido, a página oferece descarregar o que foi guardado ([[Download recovered video]]).

## Dicas {#tips}
- Use loops com o mesmo tamanho e a mesma taxa de fotogramas. Tamanhos misturados funcionam, mas fica mais calmo quando coincidem.
- Comece com 720p. Suba só quando precisar.
- Não gostou? Carregue em [[Recommended]] outra vez, mude o ambiente ou use outra semente.
- Algo errado? Veja [Ajuda e resolução de problemas](@guides/help/).

=== video-dj
name: Video DJ
title: Video DJ: misture videoclipes em dois decks
desc: Misture videoclipes completos como um DJ, com dois decks, crossfader, pré-visualização, logotipo, cartazes de texto, MIDI e uma janela de saída limpa para o projetor.
summary: Misture videoclipes em dois decks com crossfader, feito para eventos.

## O que é {#what}
O Video DJ tem dois decks para videoclipes (mp4, mov, webm). Imagem e som misturam-se em conjunto. Vê uma pré-visualização de ambos os decks ao lado da saída, e uma janela de saída separada vai para o projetor ou a televisão.

> A ferramenta é feita para um computador com Chrome ou Edge. No telemóvel obtém uma versão mais simples com dois decks, crossfader, efeitos, cartazes e uma forma de enviar a imagem para outro ecrã.

## A sua primeira mistura {#first}
1. **Adicione vídeos.** Largue videoclipes na página ou carregue em [[Add files…]]. Nomes como «Artista - Título.mp4» tornam-se o texto do cartaz. Largue um vídeo diretamente num deck para o carregar logo.
2. **Carregue os decks.** Ponha um vídeo no deck A e outro no deck B. Carregue em play em cada um.
3. **Abra a janela de saída.** Carregue em [[Open output window]], arraste a nova janela para o projetor e carregue em {{F}} para ecrã inteiro. Mantenha a janela de controlo aberta durante o show.
4. **Misture.** Mova o crossfader à mão ou carregue em [[Mix to other deck (auto fade)]] para uma transição suave. [[Fade time]] decide quanto demora.

## Auto-mix {#automix}
Ative [[Auto-mix to the next track]] e o mixer inicia a faixa seguinte no deck livre por si, alguns segundos antes de a atual acabar. Você decide quantos. Use-o em sets longos ou quando precisar de uma pausa.

## Som {#sound}
- [[Sound follows the crossfader]] faz o som fundir-se em conjunto com a imagem.
- [[Smooth (equal power)]] ou [[Linear]] decide a curva da transição de som.
- Um limitador suave no master evita que duas faixas fortes saturem ao sobrepor-se.
- [[Sound output]] permite escolher outro dispositivo de som (Chrome ou Edge).

## Logotipo e cartazes {#posters}
- **Logotipo.** Adicione um PNG com transparência (funciona melhor). O logotipo fica no canto superior direito da imagem. Escolha o tamanho e ligue-o ou desligue-o com um botão.
- **Cartazes.** Um cartaz é texto que desliza, com uma linha grande e uma pequena. Escolha uma cor predefinida, de onde entra e quanto tempo fica. Guarde cartazes em ranhuras e mostre-os com um clique ou uma tecla.
- **Nome da faixa.** Ative [[Show the track name when a track mixes in]] e o cartaz aparece sozinho.

## Controlador MIDI {#midi}
Ligue o controlador, carregue em [[Enable MIDI]] (Chrome ou Edge no computador), carregue em [[Learn]] ao lado de uma função e mova o controlo que quer usar.

## Gravar e transmitir {#record}
- [[● Record]] guarda a mistura, imagem e som, num ficheiro.
- Para transmitir, capture a janela de saída no OBS (Window Capture) ou use «Cast…» do Chrome e escolha a janela de saída. O mixer não envia vídeo pela internet por si.

## Feito para não falhar {#safe}
- As faixas são carregadas inteiras para a memória antes de tocarem (ficheiros com mais de 1,5 GB são lidos em contínuo), por isso o disco não pode interromper uma faixa.
- Um problema com um ficheiro mostra uma mensagem e nunca pára o outro deck.
- A imagem continua a correr com a janela de controlo em segundo plano, e se fechar a janela por engano, pergunta primeiro.
- Faça a verificação [Pronto para o show?](@guides/show-check/) antes de cada evento.

## A versão para telemóvel {#phone}
Dois decks, crossfader, efeitos (Zoom, Flash, Strobe, Invert, Mirror), cartazes e ecrã inteiro. Para mostrar a imagem noutro ecrã, abra [[Send to another screen]]: crie um código, abra a ligação no outro ecrã (um portátil, o navegador de uma televisão ou um computador de projetor na mesma Wi-Fi) e cole o código de resposta. Nada passa por um servidor.

> Efeitos intermitentes podem provocar crises em algumas pessoas. Mantenha-os lentos em eventos públicos.

=== vj-mixer
name: Mixer VJ
title: Mixer VJ: toque loops ao vivo com pads e camadas
desc: Toque os seus loops ao vivo. Dois canais com três camadas cada, 20 pads de loops, crossfader e efeitos que seguem o tempo.
summary: Toque loops ao vivo em 20 pads com camadas, crossfader e efeitos ao ritmo.

## O que é {#what}
O Mixer VJ serve para tocar loops de vídeo curtos ao vivo. Tem 20 pads, dois canais (A e B) com três camadas cada, um crossfader e efeitos simples que seguem o ritmo. Os loops tocam sem som.

> É feito para um computador com Chrome ou Edge. No telemóvel obtém uma versão mais pequena com 8 pads e 2 camadas por canal.

## Encha os pads {#pads}
Largue ficheiros de loops na grelha de pads ou carregue em [[Add loops…]]. Preenchem os pads vazios. Use loops mp4 (H.264) para a reprodução mais fluida. Para os reutilizar da próxima vez, ative [[Remember my loops on this computer]]. Ficam guardados só neste navegador.

## Toque {#play}
1. **Escolha uma camada.** Cada canal tem três camadas. Selecione a camada em que quer tocar.
2. **Carregue num pad** (ou na sua tecla do teclado). O loop começa logo na camada selecionada.
3. **Misture as camadas.** Cada camada tem a sua própria opacidade e um modo de mistura: normal, add, screen ou multiply.
4. **Misture os canais.** Use o crossfader ou [[Mix to other channel (auto fade)]]. [[Clear layer]] esvazia uma camada.

## O ritmo {#beat}
Os efeitos seguem um ritmo. Pode defini-lo de três maneiras:
- **Toque** no botão de tempo algumas vezes ou escreva os **BPM**.
- Deixe o mixer **ouvir o bombo** através de uma entrada de áudio ([[Audio input (kick drum)]]). Ajuste com [[Sensitivity]].
- Carregue em [[Set beat 1 (downbeat)]] no momento que deve contar como o primeiro tempo de um compasso.

## Efeitos ao ritmo {#effects}
Zoom, Shake, Flash, Strobe, Invert, Mirror, Colour spin e Blur. Ative cada um, escolha com que frequência pulsa (a cada tempo, 2 tempos ou 4 tempos) e com que força.

> Flash, Strobe e Invert a tempo rápido podem provocar crises em algumas pessoas. Mantenha lento em eventos públicos.

## Logotipo, cartazes, MIDI e saída {#more}
Funcionam como no [Video DJ](@guides/video-dj/#posters): um logotipo, cartazes de texto que deslizam, controlo MIDI com [[Learn]] e uma janela de saída para o projetor ({{F}} para ecrã inteiro). Para transmitir, capture a janela de saída no OBS ou use «Cast…» do Chrome.

## A versão para telemóvel {#phone}
8 pads, duas camadas por canal, crossfader e efeitos, com as mesmas ferramentas de ritmo. Aqui os loops também tocam sem som.

## Loops demasiado pesados? {#heavy}
Use mp4 (H.264) em 720p ou 1080p. Converta outros formatos e reduza ficheiros grandes com as [Ferramentas](@guides/tools/). Faça a verificação [Pronto para o show?](@guides/show-check/) para ver quão fluido corre o seu computador.

=== tools
name: Ferramentas de loops
title: Ferramentas de loops: converta, corrija, filtre e organize os seus loops
desc: Ferramentas gratuitas no navegador para loops de VJ: converter GIF e vídeo, criar loops perfeitos, cortar, mudar o tamanho, adicionar looks, encontrar loops gratuitos e criar pacotes.
summary: Converta, faça loops, corte, filtre, encontre e empacote os seus loops de vídeo.

## Como funcionam as ferramentas {#how}
Abra as ferramentas e escolha uma da lista. Todas seguem o mesmo padrão:
1. **Adicione ficheiros.** Largue ficheiros ou uma pasta, ou carregue em [[choose files]].
2. **Definições.** Algumas escolhas simples. As definições técnicas estão em [[Advanced]].
3. **Inicie.** O trabalho torna-se tarefas numa lista. Pode pôr muitos ficheiros em fila e deixar correr. Veja a [Fila](@guides/queue/).
4. **Descarregue.** Os resultados são ficheiros mp4 normais que pode usar em qualquer software de VJ.

Tudo corre dentro do seu navegador e os seus ficheiros nunca saem do computador. Ficheiros grandes não são problema, são lidos diretamente do disco. No Chrome ou Edge também pode escolher uma pasta e guardar cada resultado diretamente nela ([[Save each file straight into a folder I choose]]).

> A versão do navegador é mais lenta do que um programa de computador (cerca de 5 a 10 vezes). Para muitos ficheiros 4K grandes use a [versão para Linux](@guides/offline-linux/#linux), que usa o motor rápido do seu próprio computador.

## GIF to MP4 {#gif2mp4}
Converte muitos GIF para mp4 fluido de uma vez, também GIF com transparência. Para GIF transparentes, escolha uma cor de fundo (preto, branco ou #rrggbb). [[Keep shape, only shrink]] mantém pequenos os GIF pequenos. [Abrir esta ferramenta](@@tools/app/#gif2mp4).

## Make loops {#loop}
Verifica se um clipe já faz loop. Se sim, deixa-o como está. Se não, pode cortá-lo até ao melhor ponto de loop, tocá-lo para a frente e depois para trás, ou fundir o fim com o início. [[Auto: keep good loops, otherwise fix them]] escolhe por si: mantém os bons loops e corrige os outros. Pode também definir uma duração mínima, porque o Mixer mágico gosta de loops de 16 segundos ou mais. [Abrir esta ferramenta](@@tools/app/#loop).

## Convert {#convert}
Converte mov, webm, mkv, gif e outros formatos em mp4 adequado a VJ. Escolha tamanho, taxa de fotogramas e qualidade e use um [[Name template]] para renomear em massa. O modelo entende códigos como `{name}`, `{n}`, `{n2}` (um número com dois dígitos), `{w}`, `{h}`, `{res}`, `{fps}`, `{dur}` e `{date}`. Também pode remover espaços, passar para minúsculas e substituir æøå. [Abrir esta ferramenta](@@tools/app/#convert).

## Find loops {#search}
Pesquise loops em fontes gratuitas e descarregue-os e converta-os de uma vez. Internet Archive, Wikimedia Commons, NASA e os Prelinger Archives funcionam sem conta. Pexels e Pixabay têm muitos loops prontos, mas precisam de uma chave gratuita, que se obtém em um minuto. A chave fica guardada só no seu navegador e é enviada só para esse site.
- O autor e a licença de cada descarga ficam guardados num ficheiro chamado `credits.csv`. As licenças variam de clipe para clipe, por isso confirme-as antes de usar um clipe em público.
- Alguns sites não deixam uma página web descarregar os seus ficheiros. Nesse caso use [[Open page]], descarregue o clipe você mesmo e largue-o em [[Convert]].
- Descarregue só o que tem direito de usar.

[Abrir esta ferramenta](@@tools/app/#search).

## Filters {#filters}
Acrescenta looks ao estilo VJ a uma pasta inteira de loops: brilho, glitch, espelho, caleidoscópio, VHS, duotone, pixelização, rastos e mais. Carregue em [[Preview on first clip]] para ver cada look antes de os aplicar. Cada ficheiro recebe um clipe novo por cada look que escolher. [Abrir esta ferramenta](@@tools/app/#filters).

## Crop & trim {#crop}
Corta clipes para panorâmico, vertical ou quadrado e apara o início e o fim, para uma pasta inteira de uma vez. Escolha como ajustar: cortar exatamente à moldura ou acrescentar barras pretas. [Abrir esta ferramenta](@@tools/app/#crop).

## Sizes {#sizes}
Cria um proxy pequeno, 720p, 1080p e 4K de cada clipe de uma vez. Tamanhos maiores do que o original são ignorados. [Abrir esta ferramenta](@@tools/app/#sizes).

## HAP / ProRes {#pro}
Cria formatos profissionais para Resolume, VDMX, Millumin e editores de vídeo. Precisa da [versão local para Linux](@guides/offline-linux/#linux), porque usa o ffmpeg no seu próprio computador. [Abrir esta ferramenta](@@tools/app/#pro).

## Catalogue {#catalog}
Cria uma página web e um ficheiro de folha de cálculo com uma imagem, a duração, o tamanho e a qualidade de loop de cada loop. Útil para coleções grandes. [Abrir esta ferramenta](@@tools/app/#catalog).

## Loop pack {#pack}
Reúne loops num zip que pode partilhar, com imagem de pré-visualização, um ficheiro de informação e uma licença. [Abrir esta ferramenta](@@tools/app/#pack).

## Bom saber {#know}
- Os loops normalmente não têm som. [[Keep sound]] está desligado por predefinição.
- Loops curtos dão deslocação e repetição fluidas no software de VJ.
- Se algo falhar, a tarefa mostra o motivo. Veja [Ajuda e resolução de problemas](@guides/help/).

=== queue
name: Fila
title: Fila: acompanhe todos os seus trabalhos num só lugar
desc: A página Fila mostra todos os trabalhos das ferramentas e dos mixers mágicos de vídeo numa lista, para acompanhar exportações longas e descarregar os resultados.
summary: Todos os trabalhos das ferramentas e dos mixers numa lista.

## O que é a Fila {#what}
Cada tarefa longa, como converter 200 ficheiros ou exportar um vídeo de 10 minutos, torna-se um trabalho. A página Fila mostra todos os trabalhos das ferramentas e de ambos os mixers mágicos num só lugar, com o seu estado: à espera, a correr, concluído ou falhado.

## Como usar {#use}
1. Inicie trabalhos numa ferramenta ou no Mixer mágico de vídeo.
2. Abra a [Fila](@@queue/) no menu de cima. Um pequeno número junto a «Fila» indica quantos trabalhos estão a correr neste momento.
3. Descarregue os ficheiros prontos da lista quando estiverem concluídos.
4. Carregue em [[Clear finished]] para arrumar.

> Os trabalhos correm na página que os iniciou. **Mantenha essa página aberta** até dizer que está concluído. A página Fila é uma janela para os trabalhos, não os executa.

## Para onde vão os ficheiros? {#files}
Os ficheiros prontos das ferramentas ficam guardados neste navegador, até cerca de 600 MB por trabalho, para os poder descarregar mais tarde. O Mixer mágico guarda os seus próprios vídeos na sua própria página, por isso use [[Open page]] na Fila para os descarregar. Nada sai do seu computador.

Se um ficheiro já não estiver guardado, a Fila diz isso e pode repetir o trabalho.

=== show-check
name: Pronto para o show?
title: Pronto para o show? Verifique o seu dispositivo antes de ir ao vivo
desc: Uma verificação de um minuto do seu computador e navegador antes de um evento: formato de vídeo, segundo ecrã, som, bateria, velocidade e mais.
summary: Uma verificação de um minuto do seu dispositivo antes de ir ao vivo.

## O que é {#what}
Dentro do Video DJ, do Mixer VJ e das suas versões para telemóvel encontra [[Ready for the show?]]. Verifica o seu dispositivo e o navegador em um minuto e diz-lhe o que corrigir antes de o público chegar. Nada é enviado para lado nenhum.

## Como usar {#use}
1. Abra o mixer no computador que vai usar no evento, com o projetor ligado.
2. Abra [[Ready for the show?]] e leia a lista. Cada linha é [[OK]], [[Check]], [[Problem]] ou [[Info]].
3. Corrija o que for preciso e carregue em [[Run the check again]].
4. Carregue em [[Show test card]] para ver se a imagem cabe no projetor.

## O que significa cada linha {#lines}
- [[Video format]]. Se o navegador reproduz mp4 (H.264), de que os mixers mais gostam. Se não, use Chrome, Edge ou Safari, ou converta os seus vídeos com as [Ferramentas](@guides/tools/).
- [[Works without internet]]. Se o site está guardado para uso sem ligação. Veja [Sem internet e Linux](@guides/offline-linux/).
- [[Screen stays awake]]. Se o navegador consegue impedir que o ecrã adormeça. Se não, desligue a proteção de ecrã e a suspensão nas definições do sistema.
- [[Pop-up windows]]. A janela de saída é uma janela pop-up. Se o navegador bloqueia pop-ups, a janela de saída não consegue abrir.
- [[Second screen]]. Se é encontrado um segundo ecrã. Ligue primeiro o projetor.
- [[Full screen]] e [[MIDI controller]]. Se estão disponíveis e se há um controlador ligado.
- [[Sound]]. Se o som está pronto.
- [[Battery]]. Avisa se a bateria está baixa. Ligue à corrente antes do show.
- [[Speed]]. Um teste curto de quantos fotogramas por segundo o ecrã consegue desenhar. Se for lento, feche outros separadores e programas e use um tamanho de imagem menor.
- [[Free space]]. Avisa quando há pouco espaço em disco para gravar.
- [[Output window]], loops e faixas. Se a janela de saída está aberta e se algo está carregado.

## A imagem de teste {#card}
[[Show test card]] abre uma imagem feita para projetores. Se vir um círculo redondo, os quatro cantos e a moldura cor-de-rosa, a imagem cabe no ecrã. Carregue em {{F}} para ecrã inteiro e em {{Esc}} ou clique para fechar.

## Pedir ajuda com um relatório {#report}
[[Copy report]] copia um breve resumo do seu dispositivo em texto simples. Cole-o numa mensagem quando pedir ajuda com o botão **Comentários**, veja [Ajuda](@guides/help/#feedback).

=== offline-linux
name: Sem internet e Linux
title: Use o Spektronautilus sem internet, instale-o e execute-o no Linux
desc: Como fazer o site funcionar sem internet no local do evento, instalá-lo como uma app e executar o site todo localmente no Linux para mais velocidade e estabilidade.
summary: Trabalhe sem internet, instale o site como uma app ou execute-o localmente no Linux.

## Trabalhar sem internet {#offline}
O Spektronautilus guarda-se no seu navegador, por isso também funciona sem Wi-Fi no local do evento.
1. Abra o site uma vez enquanto está online.
2. Espere um minuto. As páginas e os mixers estão a ser guardados.
3. Faça [[Ready for the show?]] e veja a linha [[Works without internet]].

Também pode **instalar** o site como uma app: use «Instalar» ou «Adicionar ao ecrã inicial» no menu do navegador. Abre então na sua própria janela.

> As ferramentas carregam o seu motor de vídeo (cerca de 30 MB) na primeira vez que as usa. Use cada ferramenta uma vez enquanto está online. A versão para Linux não precisa desse motor.

## Atualizações {#updates}
Quando há uma versão nova, uma barra pequena diz [[A new version is ready.]] com os botões [[Update now]] e «Mais tarde». Nunca atualiza sozinha enquanto a página está aberta, por isso um show em curso nunca é perturbado. Atualize antes do evento, não durante.

## Versão para Linux {#linux}
Existe uma versão que executa o site todo no seu próprio computador Linux. Só é acessível a partir do seu computador (endereço 127.0.0.1) e abre no Chrome ou Chromium na sua própria janela, iniciado com definições feitas para visuais ao vivo.

Porquê usá-la:
- **Velocidade.** Se o `ffmpeg` estiver instalado, as ferramentas usam-no em vez do motor mais lento do navegador. A página diz então «Fast mode».
- **Sem limite de memória** para ficheiros grandes, e não é preciso internet (só [[Find loops]] precisa).
- **HAP e ProRes.** A [ferramenta HAP / ProRes](@guides/tools/#pro) funciona na versão para Linux.

Como instalar:
1. Descarregue o pacote para Linux (`spektronautilus-linux.tar.gz`) e descomprima-o: `tar xzf spektronautilus-linux.tar.gz`.
2. Entre na pasta e execute `./install.sh`. Não precisa de permissões de root. Acrescenta uma entrada de menu e um comando `spektronautilus`, com atalhos para o Video DJ, o Mixer VJ e as ferramentas de loops.
3. Para experimentar sem instalar, execute `./spektronautilus.py` na pasta descomprimida.
4. `./uninstall.sh` remove-o de novo.

Precisa de Python 3.8 ou superior e, para os mixers, de Chrome ou Chromium. Para ter o ffmpeg no Debian ou Ubuntu, execute `sudo apt install ffmpeg`.

## Seguro por conceção {#safe}
O servidor local só aceita pedidos do seu próprio computador, recusa outros nomes de sites e só deixa o ffmpeg mexer na sua própria pasta temporária, que é apagada quando o fecha.

=== help
name: Ajuda e resolução de problemas
title: Ajuda e resolução de problemas: quando algo não funciona
desc: Respostas a problemas comuns: vídeos que não reproduzem, a janela de saída, engasgos, um telemóvel que recarrega, MIDI, ficheiros perdidos e como entrar em contacto.
summary: Respostas a problemas comuns e como entrar em contacto.

## Um vídeo não reproduz {#play}
Quase sempre é um problema de formato. Os mixers gostam de **mp4 com H.264**. Converta o ficheiro com [[Convert]] nas [Ferramentas](@guides/tools/). Vídeos de iPhone em HEVC, alguns ficheiros mov e ficheiros webm podem dar problemas em alguns navegadores.

## Não há som {#sound}
- Os loops do Mixer VJ tocam sem som de propósito.
- No Video DJ, verifique o volume do deck, o master e [[Sound follows the crossfader]].
- O navegador pode precisar de um clique na página antes de tocar som. Clique uma vez na página.
- Verifique [[Sound output]] se usa mais de um dispositivo de som.

## A janela de saída não abre {#output}
O navegador bloqueou o pop-up. Permita pop-ups para o site e tente de novo. A verificação [Pronto para o show?](@guides/show-check/) testa isto.

## A imagem engasga {#stutter}
- Escolha um tamanho de imagem menor (o tamanho de saída) e use loops em 720p.
- Feche outros separadores e programas.
- Use um Chrome ou Edge recente e ligue o computador à corrente.
- Faça o teste de velocidade em [Pronto para o show?](@guides/show-check/).
- Num portátil, certifique-se de que o navegador usa a placa gráfica potente.

## O meu telemóvel recarrega a página {#phone}
O telefone ficou sem memória ou o ecrã bloqueou. Use um tamanho menor, 30 ou 24 fotogramas por segundo, menos loops ou mais curtos e mantenha o ecrã ligado. No iPhone, desligue o modo de poupança de energia. No Mixer mágico de vídeo, desligue a correspondência inteligente com IA.

## A exportação parou ou está muito lenta {#export}
As exportações correm em tempo real, por isso uma faixa de 10 minutos precisa de cerca de 10 minutos. Mantenha o separador aberto e visível e não deixe o computador adormecer. Se foi interrompida, o Mixer mágico de vídeo oferece recuperar o que foi guardado.

## O MIDI não encontra o meu controlador {#midi}
Use Chrome ou Edge num computador. Ligue primeiro o controlador, depois carregue em [[Enable MIDI]] e permita-o no navegador. Outros programas que usem o controlador podem bloqueá-lo, por isso feche-os.

## Onde estão os meus ficheiros? {#files}
No seu navegador, no seu computador. Os resultados prontos das ferramentas e os vídeos do Mixer mágico aparecem na página [Fila](@guides/queue/). Se apagar os dados do site no navegador, desaparecem, por isso descarregue o que quiser guardar.

## Privacidade {#privacy}
Sem contas e sem rastreamento. Vídeos e música são processados no seu dispositivo. Ao pesquisar loops contactam-se as fontes de vídeo que escolher, e o envio opcional para o Vimeo contacta o Vimeo.

## Entre em contacto {#feedback}
Carregue no botão **Comentários**, no fim de cada página, e escreva o que aconteceu. Abre o seu programa de e-mail com a mensagem pronta. Indique que navegador usa e o que estava a fazer. Num problema num computador de show, junte o relatório de [Pronto para o show?](@guides/show-check/#report). Pode também escrever-nos no [GitHub](https://github.com/munkenbissniss/spektronautilus/issues).
