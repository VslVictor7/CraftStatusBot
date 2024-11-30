@echo off
call "D:\Minecraft Servers\Status_Manager_Bot\venv\Scripts\activate.bat"
if %errorlevel% equ 0 (
    echo Ambiente Virtual Ativado > "D:\Minecraft Servers\Status_Manager_Bot\bot\log\log.txt"
) else (
    echo Falha ao ativar o ambiente virtual > "D:\Minecraft Servers\Status_Manager_Bot\bot\log\log.txt"
)
python -u --version >> "D:\Minecraft Servers\Status_Manager_Bot\bot\log\log.txt" 2>&1
python -u "D:\Minecraft Servers\Status_Manager_Bot\bot\main.py" >> "D:\Minecraft Servers\Status_Manager_Bot\bot\log\log.txt" 2>&1