@echo off
call "D:\Minecraft Servers\Status_Manager_Bot\.venv\Scripts\activate.bat"
if %errorlevel% equ 0 (
    echo Ambiente Virtual Ativado > "D:\Minecraft Servers\Status_Manager_Bot\bot\env\log.txt"
) else (
    echo Falha ao ativar o ambiente virtual > "D:\Minecraft Servers\Status_Manager_Bot\bot\env\log.txt"
)
python --version >> "D:\Minecraft Servers\Status_Manager_Bot\bot\env\log.txt" 2>&1
python "D:\Minecraft Servers\Status_Manager_Bot\bot\main.py" >> "D:\Minecraft Servers\Status_Manager_Bot\bot\env\log.txt" 2>&1