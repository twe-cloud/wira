[Setup]
AppName=Wira
AppVersion=1.0.7
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
Source: "dist\Wira\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Wira"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\app\wira_launcher.py"""; WorkingDir: "{app}\app"; IconFilename: "{app}\app\wira-icon.ico"
Name: "{autodesktop}\Wira"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\app\wira_launcher.py"""; WorkingDir: "{app}\app"; IconFilename: "{app}\app\wira-icon.ico"; Tasks: desktopicon
Name: "{userstartup}\Wira"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\app\wira_launcher.py"""; WorkingDir: "{app}\app"; IconFilename: "{app}\app\wira-icon.ico"; Tasks: startupicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional options:"
Name: "startupicon"; Description: "Start Wira when I log in"; GroupDescription: "Additional options:"; Flags: checkedonce

[Run]
Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\app\wira_launcher.py"""; WorkingDir: "{app}\app"; Description: "Launch Wira"; Flags: nowait postinstall skipifsilent
