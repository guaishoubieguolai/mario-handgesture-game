; Inno Setup安装脚本 - 马里奥手势控制游戏
; 版本: 1.0

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName=Mario Hand Gesture Game
AppVersion=1.0.0
AppVerName=Mario Hand Gesture Game 1.0
AppPublisher=Mario Hand Gesture Game Team
DefaultDirName={autopf}\MarioHandGesture
DefaultGroupName=Mario Hand Gesture
AllowNoIcons=yes
LicenseFile=build_tools\LICENSE.txt
InfoBeforeFile=build_tools\README.txt
OutputDir=.
OutputBaseFilename=MarioHandGesture_Setup
SetupIconFile=resources\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

; 安装界面设置
SetupStyle=modern
WizardImageStretch=yes

; 许可协议
UninstallDisplayIcon={app}\MarioHandGesture.exe
UninstallDisplayName=Mario Hand Gesture Game

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 复制exe文件
Source: "dist\MarioHandGesture.exe"; DestDir: "{app}"; Flags: ignoreversion
; 复制README和LICENSE
Source: "build_tools\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "build_tools\README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 开始菜单快捷方式
Name: "{group}\Mario Hand Gesture"; Filename: "{app}\MarioHandGesture.exe"
Name: "{group}\{cm:UninstallProgram,Mario Hand Gesture}"; Filename: "{uninstallexe}"

; 桌面快捷方式
Name: "{autodesktop}\Mario Hand Gesture"; Filename: "{app}\MarioHandGesture.exe"; Tasks: desktopicon

[Run]
; 安装完成后运行的选项
Filename: "{app}\MarioHandGesture.exe"; Description: "{cm:LaunchProgram,Mario Hand Gesture}"; Flags: nowait postinstall skipifsilent

[Registry]
; 添加到添加/删除程序
Root: HKLM; Subkey: "Software\MarioHandGesture"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\MarioHandGesture"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"

[Code]
// 卸载前确认
function InitializeUninstall(): Boolean;
begin
    Result := True;
    if MsgBox('确定要卸载 Mario Hand Gesture Game 吗？', mbConfirmation, MB_YESNO) = IDNO then
        Result := False;
end;
