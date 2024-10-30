import requests
from win10toast import ToastNotifier

def get_public_ipv4():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        ip_address = response.json().get("ip")
        return ip_address
    except requests.RequestException as e:
        return f"Erro ao obter meu ip: {e}"

if __name__ == "__main__":
    ip = get_public_ipv4()
    message = f"{ip}"

    toaster = ToastNotifier()
    toaster.show_toast("Endereço IP Público", message, duration=60)
