[Setup]
AppName=MyFoxyPDF
AppVersion=1.0
DefaultDirName={pf}\MyFoxyPDF
DefaultGroupName=MyFoxyPDF
OutputBaseFilename=MyFoxyPDF_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\MyFoxyPDF\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\MyFoxyPDF"; Filename: "{app}\MyFoxyPDF.exe"
Name: "{commondesktop}\MyFoxyPDF"; Filename: "{app}\MyFoxyPDF.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Registry]
Root: HKCR; Subkey: ".pdf"; ValueType: string; ValueName: ""; ValueData: "MyFoxyPDF.pdf"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "MyFoxyPDF.pdf"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekey
Root: HKCR; Subkey: "MyFoxyPDF.pdf\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\MyFoxyPDF.exe"" ""%1"""; Flags: uninsdeletevalue
