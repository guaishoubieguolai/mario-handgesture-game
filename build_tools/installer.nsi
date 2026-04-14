; NSIS安装程序脚本 - 马里奥手势控制游戏
; 版本: 1.0

; 基本设置
Name "Mario Hand Gesture Game"
OutFile "MarioHandGesture_Setup.exe"
InstallDir "$PROGRAMFILES64\MarioHandGesture"
InstallDirRegKey HKLM "Software\MarioHandGesture" "Install_Dir"
RequestExecutionLevel admin

; 界面设置
!include "MUI2.nsh"

; 安装页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "build_tools\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; 语言
!insertmacro MUI_LANGUAGE "SimpChinese"

; 版本信息
VIProductVersion "1.0.0.0"
VIAddVersionKey /PRODUCT "Mario Hand Gesture Game"
VIAddVersionKey /VERSION "1.0"

; 安装内容
Section "主程序" SecMain
    SectionIn RO
    
    ; 设置安装目录
    SetOutPath $INSTDIR
    
    ; 复制exe文件
    File "dist\MarioHandGesture.exe"
    
    ; 创建卸载程序
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; 创建桌面快捷方式
    CreateDirectory "$SMPROGRAMS\Mario Hand Gesture"
    CreateShortcut "$SMPROGRAMS\Mario Hand Gesture\Mario Hand Gesture.lnk" "$INSTDIR\MarioHandGesture.exe"
    CreateShortcut "$SMPROGRAMS\Mario Hand Gesture\卸载.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortcut "$DESKTOP\Mario Hand Gesture.lnk" "$INSTDIR\MarioHandGesture.exe"
    
    ; 写入注册表
    WriteRegStr HKLM "Software\MarioHandGesture" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarioHandGesture" "DisplayName" "Mario Hand Gesture Game"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarioHandGesture" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarioHandGesture" "DisplayIcon" "$INSTDIR\MarioHandGesture.exe"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarioHandGesture" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarioHandGesture" "NoRepair" 1
SectionEnd

; 卸载内容
Section "Uninstall"
    ; 删除文件
    Delete "$INSTDIR\MarioHandGesture.exe"
    Delete "$INSTDIR\Uninstall.exe"
    
    ; 删除快捷方式
    Delete "$DESKTOP\Mario Hand Gesture.lnk"
    Delete "$SMPROGRAMS\Mario Hand Gesture\Mario Hand Gesture.lnk"
    Delete "$SMPROGRAMS\Mario Hand Gesture\卸载.lnk"
    RMDir "$SMPROGRAMS\Mario Hand Gesture"
    
    ; 删除安装目录
    RMDir "$INSTDIR"
    
    ; 删除注册表
    DeleteRegKey HKLM "Software\MarioHandGesture"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarioHandGesture"
SectionEnd

; 安装完成后运行
Function .onInstSuccess
    MessageBox MB_OK "安装完成！$\n$\n点击确定启动游戏。" IDOK LaunchApp
    LaunchApp:
        Exec "$INSTDIR\MarioHandGesture.exe"
FunctionEnd
