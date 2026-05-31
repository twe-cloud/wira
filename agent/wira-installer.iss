[Setup]
AppName=Wira
AppVersion=1.0.2
AppPublisher=Ni Biashara LLC
AppPublisherURL=https://nibiashara.biz/products/wira/
DefaultDirName={autopf}\Wira
DefaultGroupName=Wira
OutputDir=dist
OutputBaseFilename=WiraSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Files]
Source: "dist\Wira.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Wira"; Filename: "{app}\Wira.exe"
Name: "{autodesktop}\Wira"; Filename: "{app}\Wira.exe"; Tasks: desktopicon
Name: "{userstartup}\Wira"; Filename: "{app}\Wira.exe"; Tasks: startupicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional options:"
Name: "startupicon"; Description: "Start Wira when I log in"; GroupDescription: "Additional options:"; Flags: checkedonce

[Run]
Filename: "{app}\Wira.exe"; Description: "Launch Wira"; Flags: nowait postinstall skipifsilent
