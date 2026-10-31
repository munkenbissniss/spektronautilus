; Inno Setup script: builds Spektronautilus-Setup.exe from build\win\spektronautilus (see windows\build_windows.py).
; No administrator rights needed: it installs for the current user.
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif
[Setup]
AppId={{6B0B3E36-5A7C-4E0F-9E1D-5E6B7A1D0C42}
AppName=Spektronautilus
AppVersion={#AppVersion}
AppPublisher=Spektronautilus
AppPublisherURL=https://munkenbissniss.github.io/spektronautilus/
DefaultDirName={autopf}\Spektronautilus
DefaultGroupName=Spektronautilus
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\build
OutputBaseFilename=Spektronautilus-Setup
SetupIconFile=spektronautilus.ico
UninstallDisplayIcon={app}\spektronautilus.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=..\LICENSE
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
[Tasks]
Name: "desktop"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
[Files]
Source: "..\build\win\spektronautilus\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
[Icons]
Name: "{group}\Spektronautilus"; Filename: "{app}\spektronautilus.exe"; IconFilename: "{app}\spektronautilus.ico"; Flags: runminimized
Name: "{group}\Video DJ"; Filename: "{app}\spektronautilus.exe"; Parameters: "--path live-dj/"; IconFilename: "{app}\spektronautilus.ico"; Flags: runminimized
Name: "{group}\VJ Mixer"; Filename: "{app}\spektronautilus.exe"; Parameters: "--path vj-pad/"; IconFilename: "{app}\spektronautilus.ico"; Flags: runminimized
Name: "{group}\Magic Video Mixer"; Filename: "{app}\spektronautilus.exe"; Parameters: "--path mixer/"; IconFilename: "{app}\spektronautilus.ico"; Flags: runminimized
Name: "{group}\Loop tools"; Filename: "{app}\spektronautilus.exe"; Parameters: "--path tools/app/"; IconFilename: "{app}\spektronautilus.ico"; Flags: runminimized
Name: "{group}\Uninstall Spektronautilus"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Spektronautilus"; Filename: "{app}\spektronautilus.exe"; IconFilename: "{app}\spektronautilus.ico"; Tasks: desktop; Flags: runminimized
[Run]
Filename: "{app}\spektronautilus.exe"; Description: "{cm:LaunchProgram,Spektronautilus}"; Flags: nowait postinstall skipifsilent runminimized
