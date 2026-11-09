; Instalador do Conversor Markdown para Windows (Inno Setup 6).
; Instala só para o usuário atual, sem pedir senha de administrador,
; em %LOCALAPPDATA%\Programs\Conversor Markdown, e aparece em "Aplicativos instalados".
;
; Uso: iscc /DVersao=1.3.0 /DOrigem="C:\caminho\Conversor Markdown" build\instalador.iss
; (Origem é a pasta gerada pelo PyInstaller, a mesma que vai no .zip portátil.)

#ifndef Versao
  #define Versao "0.0.0"
#endif
#ifndef Origem
  #error Informe /DOrigem com a pasta do programa gerada pelo PyInstaller
#endif

[Setup]
; não troque o AppId: é ele que liga as versões novas à instalação anterior
AppId={{6F2C1B7A-3E0D-4C59-9A8E-4B1D2F7C8E31}
AppName=Conversor Markdown
AppVersion={#Versao}
AppVerName=Conversor Markdown {#Versao}
AppPublisher=n-lobato
AppPublisherURL=https://github.com/n-lobato/conversor-markdown
AppSupportURL=https://github.com/n-lobato/conversor-markdown/issues
AppUpdatesURL=https://github.com/n-lobato/conversor-markdown/releases
VersionInfoVersion={#Versao}
DefaultDirName={autopf}\Conversor Markdown
DefaultGroupName=Conversor Markdown
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
LicenseFile=..\LICENSE
SetupIconFile=..\assets\icone.ico
UninstallDisplayIcon={app}\Conversor Markdown.exe
UninstallDisplayName=Conversor Markdown
OutputDir=..\dist
OutputBaseFilename=Conversor-Markdown-v{#Versao}-windows-x64-instalador
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes

[Languages]
Name: "ptbr"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[InstallDelete]
; numa atualização, apaga a pasta interna antiga para não sobrar biblioteca de outra versão
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "{#Origem}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Conversor Markdown"; Filename: "{app}\Conversor Markdown.exe"
Name: "{autodesktop}\Conversor Markdown"; Filename: "{app}\Conversor Markdown.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Conversor Markdown.exe"; Description: "{cm:LaunchProgram,Conversor Markdown}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; as opções lembradas pela janela (só caixas de marcar)
Type: filesandordirs; Name: "{userappdata}\Conversor Markdown"
