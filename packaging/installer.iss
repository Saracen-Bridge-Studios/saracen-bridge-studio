; Inno Setup script: wraps dist\SaracenBridgeStudio into one Windows installer.
; Build:  iscc packaging\installer.iss   (after PyInstaller; Inno Setup 6.5+)
#define AppVersion GetEnv("STUDIO_VERSION")
#if AppVersion == ""
  #define AppVersion "1.1.2"
#endif

; Gemma (optional) is NOT downloaded by this installer any more (1.0.2). On Jon's PC, 13 Oct, the installer's own
; downloader stalled on the 6.1 GB model ("Error reading data: (12002) The operation timed out") and could only start
; the file again from zero. The installer now records the choice in {app}\llm\wanted.json and the Studio downloads the
; engine, the model and its vision add-on itself, in the background, resuming from the last byte after a dropped
; connection or a restart, each file checked against its SHA-256 (engine/studio/fetch.py holds the sources).
#define G12_FILE "gemma-4-12b-it-qat-q4_0.gguf"
#define E4B_FILE "gemma-4-E4B_q4_0-it.gguf"
#define G12_VIS_FILE "mmproj-gemma-4-12b-it-qat-q4_0.gguf"
#define E4B_VIS_FILE "gemma-4-E4B-it-mmproj.gguf"

[Setup]
AppId={{6C1E5B7A-4E1D-4A8C-9B1F-5A2B3C4D5E60}
AppName=Saracen Bridge Studio
AppVersion={#AppVersion}
AppPublisher=Saracen Bridge Ltd
DefaultDirName={autopf}\Saracen Bridge Studio
DefaultGroupName=Saracen Bridge Studio
OutputDir=..\dist\installer
OutputBaseFilename=SaracenBridgeStudio-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
; A model packed inside the installer would push it past Inno Setup's 4.2 GB single-file limit. The build script
; then sets STUDIO_SPAN=1 and Setup.exe ships with Setup-1.bin beside it. (The default build downloads it instead.)
#if GetEnv("STUDIO_SPAN") == "1"
DiskSpanning=yes
DiskSliceSize=max
#endif
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
WizardStyle=modern
; Saracen Bridge purple logo: program icon, installer icon and wizard panels
SetupIconFile=studio.ico
UninstallDisplayIcon={app}\SaracenBridgeStudio.exe
WizardImageFile=brand\wizard_large.bmp
WizardSmallImageFile=brand\wizard_small.bmp

[InstallDelete]
; Upgrades replace the program files completely. The AI engine ({app}\llm) and user data (%APPDATA%\SaracenStudio)
; are left alone, so an upgrade never deletes a multi-GB model download.
Type: filesandordirs; Name: "{app}\_internal"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\llm"

[Files]
Source: "..\dist\SaracenBridgeStudio\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
; Microsoft's WebView2 Evergreen Bootstrapper (signed by Microsoft, ~2 MB). Unpacked and run only when the runtime is missing.
; Build requirement: place it at packaging\redist\MicrosoftEdgeWebview2Setup.exe (https://go.microsoft.com/fwlink/p/?LinkId=2124703).
Source: "redist\MicrosoftEdgeWebview2Setup.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: NeedsWebView2
; Licences for the AI engine and Gemma, placed when Gemma is chosen (the Studio downloads the files themselves)
Source: "llm\LICENSE-Gemma.txt"; DestDir: "{app}\llm"; Flags: ignoreversion; Check: GemmaChosen
Source: "llm\LICENSE-llama.cpp.txt"; DestDir: "{app}\llm"; Flags: ignoreversion; Check: GemmaChosen

[Icons]
Name: "{group}\Saracen Bridge Studio"; Filename: "{app}\SaracenBridgeStudio.exe"
Name: "{autodesktop}\Saracen Bridge Studio"; Filename: "{app}\SaracenBridgeStudio.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Run]
Filename: "{tmp}\MicrosoftEdgeWebview2Setup.exe"; Parameters: "/silent /install"; StatusMsg: "Installing Microsoft Edge WebView2 Runtime..."; Flags: waituntilterminated; Check: NeedsWebView2
Filename: "{app}\SaracenBridgeStudio.exe"; Description: "Launch Saracen Bridge Studio"; Flags: nowait postinstall skipifsilent

[Code]
{ ---------------------------------------------------------------- WebView2
  Microsoft's documented check: the runtime is present when pv exists and is not 0.0.0.0 under one of these keys.
  Without it the app still works: it opens in the default browser. }
function RuntimeVersion(Root: Integer; Key: String): String;
begin
  if not RegQueryStringValue(Root, Key, 'pv', Result) then
    Result := '';
end;

function HasRuntime(V: String): Boolean;
begin
  Result := (V <> '') and (V <> '0.0.0.0');
end;

function NeedsWebView2: Boolean;
var
  Id: String;
begin
  Id := '{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';
  Result := not (HasRuntime(RuntimeVersion(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\' + Id))
              or HasRuntime(RuntimeVersion(HKLM, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\' + Id))
              or HasRuntime(RuntimeVersion(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\' + Id)));
end;

{ ---------------------------------------------------------------- Gemma page: install it, or skip }
type
  TMemoryStatusEx = record
    dwLength: Cardinal;
    dwMemoryLoad: Cardinal;
    ullTotalPhys: Int64;
    ullAvailPhys: Int64;
    ullTotalPageFile: Int64;
    ullAvailPageFile: Int64;
    ullTotalVirtual: Int64;
    ullAvailVirtual: Int64;
    ullAvailExtendedVirtual: Int64;
  end;

function GlobalMemoryStatusEx(var lpBuffer: TMemoryStatusEx): Boolean;
  external 'GlobalMemoryStatusEx@kernel32.dll stdcall';

const
  OPT_12B = 0;
  OPT_E4B = 1;
  OPT_SKIP = 2;

var
  GemmaPage: TInputOptionWizardPage;
  ChoiceFromParam: Boolean;

function MemoryGB: Integer;
var
  M: TMemoryStatusEx;
begin
  M.dwLength := 64;
  if GlobalMemoryStatusEx(M) then
    Result := Integer(M.ullTotalPhys div 1073741824)
  else
    Result := 0;
end;

function ModelPath(Name: String): String;
begin
  Result := AddBackslash(WizardDirValue) + 'llm\models\' + Name;
end;

function InstalledGemma: String;
begin
  if FileExists(ModelPath('{#G12_FILE}')) then
    Result := 'Gemma 4 12B'
  else if FileExists(ModelPath('{#E4B_FILE}')) then
    Result := 'Gemma 4 E4B'
  else
    Result := '';
end;

procedure InitializeWizard;
var
  P: String;
begin
  GemmaPage := CreateInputOptionPage(wpSelectTasks,
    'AI engine for written coverage',
    'Install Gemma, the AI that writes script coverage on this computer?',
    'Gemma runs entirely on this PC: scripts never leave it. After setup, Saracen Bridge Studio downloads it ' +
    'in the background from Google''s official source and checks it before use. If the connection drops or the ' +
    'Studio is closed, it carries on from where it stopped. Everything else works meanwhile, and Gemma can also ' +
    'be added later from Settings.',
    True, False);
  GemmaPage.Add('Install Gemma 4 12B  (recommended: best writing. 7.2 GB download, vision included; for PCs with 16 GB memory or more)');
  GemmaPage.Add('Install Gemma 4 E4B  (lighter. 6.1 GB download, vision included; for PCs with 8 GB memory)');
  GemmaPage.Add('Skip for now');

  P := Lowercase(ExpandConstant('{param:GEMMA|}'));
  ChoiceFromParam := True;
  if P = '12b' then GemmaPage.SelectedValueIndex := OPT_12B
  else if P = 'e4b' then GemmaPage.SelectedValueIndex := OPT_E4B
  else if P = 'skip' then GemmaPage.SelectedValueIndex := OPT_SKIP
  else begin
    ChoiceFromParam := False;
    if WizardSilent then
      GemmaPage.SelectedValueIndex := OPT_SKIP        { silent installs never start a multi-GB download unasked }
    else if MemoryGB >= 15 then
      GemmaPage.SelectedValueIndex := OPT_12B
    else
      GemmaPage.SelectedValueIndex := OPT_E4B;
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
var
  Have: String;
begin
  if CurPageID = GemmaPage.ID then begin
    Have := InstalledGemma;
    if Have <> '' then begin
      GemmaPage.CheckListBox.ItemCaption[OPT_SKIP] := 'Keep the ' + Have + ' already installed';
      if not ChoiceFromParam then
        GemmaPage.SelectedValueIndex := OPT_SKIP;
    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  { Ask only a person clicking through; a silent install with /GEMMA= has already decided. }
  if (CurPageID = GemmaPage.ID) and (GemmaPage.SelectedValueIndex = OPT_12B) and (MemoryGB > 0) and (MemoryGB < 12)
     and not WizardSilent and not ChoiceFromParam then
    Result := SuppressibleMsgBox('This computer has about ' + IntToStr(MemoryGB) + ' GB of memory. Gemma 4 12B needs about ' +
                     '16 GB to run well; Gemma 4 E4B suits this computer better.' + #13#10#13#10 + 'Install 12B anyway?',
                     mbConfirmation, MB_YESNO, IDYES) = IDYES;
end;

function GemmaChosen: Boolean;
begin
  Result := GemmaPage.SelectedValueIndex <> OPT_SKIP;
end;

function HasVision(Which: String): Boolean;
begin
  if Which = '12b' then Result := FileExists(ModelPath('{#G12_VIS_FILE}')) else Result := FileExists(ModelPath('{#E4B_VIS_FILE}'));
end;

function WantedModel: String;
{ What the Studio should fetch: the chosen model, or the kept one when its vision add-on is missing. }
begin
  Result := '';
  case GemmaPage.SelectedValueIndex of
    OPT_12B: Result := '12b';
    OPT_E4B: Result := 'e4b';
  else
    if FileExists(ModelPath('{#G12_FILE}')) and not HasVision('12b') then Result := '12b'
    else if FileExists(ModelPath('{#E4B_FILE}')) and not HasVision('e4b') then Result := 'e4b';
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  M: String;
begin
  if CurStep = ssPostInstall then begin
    M := WantedModel;
    if M <> '' then begin
      ForceDirectories(ExpandConstant('{app}\llm'));
      SaveStringToFile(ExpandConstant('{app}\llm\wanted.json'), '{"model": "' + M + '", "from": "installer"}', False);
    end
    else if (GemmaPage.SelectedValueIndex = OPT_SKIP) and (InstalledGemma = '') then
      DeleteFile(ExpandConstant('{app}\llm\wanted.json'));     { "Skip for now" stops an earlier, unfinished request }
  end;
end;

function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo, MemoTypeInfo, MemoComponentsInfo,
  MemoGroupInfo, MemoTasksInfo: String): String;
var
  Engine: String;
begin
  Result := MemoDirInfo + NewLine + NewLine;
  if MemoGroupInfo <> '' then
    Result := Result + MemoGroupInfo + NewLine + NewLine;
  if MemoTasksInfo <> '' then
    Result := Result + MemoTasksInfo + NewLine + NewLine;
  case GemmaPage.SelectedValueIndex of
    OPT_12B: if FileExists(ModelPath('{#G12_FILE}')) then Engine := 'Gemma 4 12B (already downloaded)' else Engine := 'Gemma 4 12B with vision (7.2 GB, downloaded by the Studio after setup)';
    OPT_E4B: if FileExists(ModelPath('{#E4B_FILE}')) then Engine := 'Gemma 4 E4B (already downloaded)' else Engine := 'Gemma 4 E4B with vision (6.1 GB, downloaded by the Studio after setup)';
  else
    if InstalledGemma <> '' then begin
      Engine := 'Keep the ' + InstalledGemma + ' already installed';
      if WantedModel <> '' then Engine := Engine + ', and the Studio adds its vision add-on for Look Book Analytics';
    end
    else Engine := 'None for now (written coverage needs one; add it later from Settings)';
  end;
  Result := Result + 'AI engine:' + NewLine + Space + Engine;
end;
