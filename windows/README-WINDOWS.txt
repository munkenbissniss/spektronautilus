Spektronautilus for Windows
===========================
The whole site on your own computer. It works offline (only "Find loops" needs the internet) and your files never leave the computer.

START
  Use the Start menu: Spektronautilus, Video DJ, VJ Mixer, Magic Video Mixer or Loop tools.
  A small black window opens in the taskbar. That is the program running. Close it to quit.
  The site opens in Chrome or Edge in its own window. Edge is already part of Windows.

WHAT YOU GET COMPARED WITH THE WEB VERSION
  * Fast converting with the bundled ffmpeg (no memory limit for big files).
  * HAP and ProRes, if the bundled ffmpeg supports them (the tool tells you).
  * A browser window started with settings made for live visuals.
  AI upscaling and AI slow motion, if you install Video2X (a separate free programme, not included). It needs a graphics card with Vulkan.
  If Spektronautilus does not find it, write the full path to video2x.exe on one line in a text file called
  video2x.txt in the folder %APPDATA%\spektronautilus, then start Spektronautilus again.

WINDOWS SAYS "UNKNOWN PUBLISHER" OR SMARTSCREEN WARNS
  The installer is not code-signed. Choose "More info" and then "Run anyway".

SETTINGS
  Your settings and loops are kept by the browser, per port. Keep the same port (default 8765).
  Command line: spektronautilus.exe --port 9000 --window --no-browser --path live-dj/

FFMPEG
  The ffmpeg in the "ffmpeg" folder is a separate program under its own licence (see ffmpeg\LICENSE-ffmpeg.txt).
  To use your own, put ffmpeg.exe in that folder.

REMOVE
  Settings > Apps > Spektronautilus > Uninstall.
