Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\Users\NomeDoUsuario\Desktop\script.bat""", 0, False

' Mudaro diretorio dentro do .Run para a path do script.bat, exemplo abaixo:
' WshShell.Run """C:\Users\NomeDoUsuario\Desktop\script.bat""", 0, False
