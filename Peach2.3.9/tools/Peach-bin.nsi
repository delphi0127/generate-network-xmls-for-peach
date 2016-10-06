;
; Peach Windows x86 Binary Installer
;
; Copyright (c) Michael Eddington
;
; Permission is hereby granted, free of charge, to any person obtaining a copy 
; of this software and associated documentation files (the "Software"), to deal
; in the Software without restriction, including without limitation the rights 
; to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
; copies of the Software, and to permit persons to whom the Software is 
; furnished to do so, subject to the following conditions:
;
; The above copyright notice and this permission notice shall be included in	
; all copies or substantial portions of the Software.
;
; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
; IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
; FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
; AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
; LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
; OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
; SOFTWARE.
;
; Authors:
;   Michael Eddington (mike@phed.org)
;
; $Id: Peach.nsi 1269 2008-10-13 04:30:39Z meddingt $
;

;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;General

  ;Name and file
  Name "Peach 2.3.8 x86"
  OutFile "Peach-2.3.8-x86.exe"

  ;Default installation folder
  InstallDir "c:\peach"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Peach" ""

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

;  !insertmacro MUI_PAGE_LICENSE "${NSISDIR}\Docs\Modern UI\License.txt"
;  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Dummy Section" SecDummy
  
  SetOutPath "$INSTDIR"
  
  ;ADD YOUR OWN FILES HERE...
  File /r /x docs /x .svn /x peach.py /x *.pyw /x *.ncb \
    /x *.pch /x dependencies /x test /x Peach /x Peach-2*.exe \
    /x logtest /x build.bat /x gendocs.bat \
    /x *.nsi /x PeachSimple.gadget \
    /x setup.py /x peach.kpf \
    /x compilepeach.py /x deb-ubuntu \
    /x tools\minset \
    c:\peach\*.*
  
  ; Remove old links
  RMDir /r "$SMPROGRAMS\Peach"
  ; Add program menu links
  CreateDirectory "$SMPROGRAMS\Peach"
  CreateShortCut "$SMPROGRAMS\Peach\Peach Documentation.lnk" "http://peachfuzzer.com" "" "$INSTDIR\bin\icons\peach20x20.ico"
  CreateShortCut "$SMPROGRAMS\Peach\Peach Validator.lnk" "$INSTDIR\bin\peachvalidator.exe" "" "$INSTDIR\bin\icons\peach20x20.ico"
  CreateShortCut "$SMPROGRAMS\Peach\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  ;Store installation folder
  WriteRegStr HKCU "Software\Peach" "" $INSTDIR
  
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecDummy ${LANG_ENGLISH} "A test section."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ; Unregister com
  ;UnRegDLL "$INSTDIR\bin\DbgEngEvent.dll"
  
  Delete "$INSTDIR\Uninstall.exe"

  ; Remove it all baby!!!
  RMDir /r "$INSTDIR"
  RMDir /r "$SMPROGRAMS\Peach"

  DeleteRegKey /ifempty HKCU "Software\Peach"

SectionEnd

; end
