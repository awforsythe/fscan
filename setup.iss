#define ApplicationVersion GetEnv('FSCAN_INSTALLER_VERSION')

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{45131461-F27C-48DC-AE29-4BDA32CBB3AC}
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

[Code]
var
  EnvironmentPage: TInputQueryWizardPage;

procedure AddEnvironmentPage();
begin
  EnvironmentPage := CreateInputQueryPage(
    wpSelectDir,
    'Configure Environment',
    'Evironment variables can be changed in Windows (via Advanced System Settings) at any time.', '');
  EnvironmentPage.Add('FSCAN_TESTVAR', False);
  EnvironmentPage.Values[0] := GetEnv('FSCAN_TESTVAR');
  if EnvironmentPage.Values[0] = '' then EnvironmentPage.Values[0] := 'something';
end;

procedure InitializeWizard();
begin
  AddEnvironmentPage();
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'FSCAN_TESTVAR', EnvironmentPage.Values[0]);
  end;
end;
