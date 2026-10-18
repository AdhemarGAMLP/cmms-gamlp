; Script generado para SGEM GAMLP v1.2
; Sistema de Gestión de Equipamiento Médico - GAMLP

#define MyAppName "SGEM GAMLP"
#define MyAppVersion "1.2"
#define MyAppPublisher "Gobierno Autonomo Municipal de La Paz (GAMLP)"
#define MyAppURL "https://cmms-gamlp.onrender.com"
#define MyAppExeName "SGEM_GAMLP_v1.2.exe"

[Setup]
AppId={{D82F7A41-9C3E-4D7A-9A2E-8B5D3F6A7B1C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes

; Carpeta de salida para el Instalador V1.2
OutputDir=C:\Users\HP\Desktop\GAMLP_SGEM\instalador V1.2
OutputBaseFilename=Instalador_SGEM_GAMLP_v1.2
SolidCompression=yes
WizardStyle=modern dynamic

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; 1. Ejecutable compilado desde dist de CMMS_GAMLP
Source: "C:\Users\HP\Desktop\CMMS_GAMLP\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 2. Carpeta de plantillas Excel oficiales
Source: "C:\Users\HP\Desktop\CMMS_GAMLP\plantillas\*"; DestDir: "{app}\plantillas"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Dirs]
; Crear automáticamente la carpeta de datos de gestión en el escritorio del usuario
Name: "{userdesktop}\Datos_De_Gestion_GAMLP"
