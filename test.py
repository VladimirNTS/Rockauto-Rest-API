import httpx

proxy = "socks5://pcIJMsXmT6:PC_3PtA4vMPRC8M883OE@51.77.190.247:5959"

with httpx.Client(proxy=proxy, timeout=20.0) as client:
    r = client.get("https://api.ipify.org?format=json")
    print(r.text)
