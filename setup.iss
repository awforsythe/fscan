#define ApplicationVersion GetEnv('FSCAN_INSTALLER_VERSION')

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{280EA681-E7F6-4F6F-88C4-007703EE7677}
AppName=FScan
AppVersion={#ApplicationVersion}
DefaultDirName={%USERPROFILE}\FScan
DisableProgramGroupPage=yes
OutputDir={#SourcePath}\dist
OutputBaseFilename=Install_FScan_v{#ApplicationVersion}
Compression=lzma
SolidCompression=yes
SetupIconFile={#SourcePath}\res\install_icon.ico
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourcePath}\dist\FScan\FScan.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\dist\FScan\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{commonprograms}\FScan"; Filename: "{app}\FScan.exe"
Name: "{commondesktop}\FScan"; Filename: "{app}\FScan.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\FScan.exe"; Description: "{cm:LaunchProgram,FScan}"; Flags: nowait postinstall
