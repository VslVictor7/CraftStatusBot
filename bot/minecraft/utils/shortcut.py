import win32com.client

def resolve_shortcut(shortcut_path):
    shell = win32com.client.Dispatch("WScript.Shell")
    real_path = shell.CreateShortcut(shortcut_path).TargetPath
    return real_path