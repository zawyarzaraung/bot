import os
import requests
import re
from datetime import datetime

# Headers for checking streams (Avoid 403 Forbidden)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# ⚽ နိုင်ငံတကာ အများသုံး လိုင်းများ၏ တရားဝင် Logo URLs (Open-source Links)
LOGO_DATABASE = {
    "fifa plus": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/fifa-plus.png",
    "fox sports 2": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/fox-sports-2.png",
    "tyc sports": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/tyc-sports.png",
    "dsports": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/dsports.png",
    "caze tv": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/caze-tv.png",
    "dazn 1": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/dazn-1.png",
    "dazn 2": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/dazn-2.png",
    "dazn 3": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/dazn-3.png",
    "dazn 4": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/dazn-4.png",
    "dazn 5": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/dazn-5.png",
    "bein sports 1": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/bein-sports-1.png",
    "bein sports 2": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/bein-sports-2.png",
    "bein sports 3": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/bein-sports-3.png",
    "bein sports 4": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/bein-sports-4.png",
    "bein sports xtra": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/bein-sports-xtra.png",
    "bein sports": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/bein-sports.png",
    "tudn": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/tudn.png",
    "cricbuzz": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/cricbuzz.png",
    "willow hd": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/willow-tv.png",
    "t sports": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/t-sports.png",
    "euro tv": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/euro-sport.png",
    "star sports 1": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/star-sports-1.png",
    "star sports": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/star-sports.png",
    "cricket gold": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/cricket-gold.png",
    "espn": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/espn.png",
    "asports": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/a-sports.png",
    "ptv sports": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/ptv-sports.png",
    "tsn 1": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/tsn-1.png",
    "tsn 2": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/tsn-2.png",
    "tsn 3": "https://raw.githubusercontent.com/manandbytes/iptv-logos/main/logos/tsn-3.png"
}

def clean_channel_name(name):
    """လိုင်းနာမည်ထဲမှ ပိုနေသော အမှိုက်စာလုံးများကို ရှင်းလင်းပေးရန်"""
    name = name.lower()
    # HD, SD, FHD, 1080p, [ARG], 🇦🇷 စသည့် သင်္ကေတများကို ဖယ်ထုတ်ခြင်း
    name = re.sub(r'\[.*?\]|\(.*?\)|hd|sd|fhd|1080p|720p|backup|-', '', name)
    name = re.sub(r'[^\w\s]', '', name) # အီမိုဂျီနှင့် အထူးစာလုံးများ ဖယ်ရှားရန်
    return name.strip()

def get_matched_logo(info_line):
    """EXTINF ထဲက လိုင်းနာမည်ကို ယူပြီး Logo တွဲပေးရန်"""
    name_match = info_line.split(',')[-1].strip()
    cleaned_name = clean_channel_name(name_match)
    
    # Fuzzy Matching Logic (နာမည် တစ်စိတ်တစ်ပိုင်း တူရင် ပုံတွဲပေးမည်)
    for db_name, logo_url in LOGO_DATABASE.items():
        if db_name in cleaned_name or cleaned_name in db_name:
            return logo_url
    return None

def inject_logo(info_line, logo_url):
    """EXTINF ထဲသို့ tvg-logo tag ကို ထည့်သွင်းပေးရန်"""
    if not logo_url:
        return info_line
        
    # tvg-logo ရှိပြီးသားဆိုလျှင် အသစ်မထည့်ဘဲ မူလအတိုင်း ထားမည်
    if 'tvg-logo=' in info_line:
        return info_line
        
    if info_line.startswith('#EXTINF:'):
        parts = info_line.split(',', 1)
        extinf_part = parts[0]
        updated_extinf = f'{extinf_part} tvg-logo="{logo_url}"'
        if len(parts) > 1:
            return f'{updated_extinf},{parts[1]}'
        return updated_extinf
    return info_line

def parse_m3u(file_path):
    channels = []
    if not os.path.exists(file_path):
        return channels
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    matches = re.findall(r'(#EXTINF:.*?\n)(http.*?)(?=\n#EXTINF:|\n$|$)', content, re.DOTALL)
    for info, link in matches:
        channels.append({
            'info': info.strip(),
            'link': link.strip()
        })
    return channels

def check_stream(link):
    try:
        response = requests.head(link, headers=HEADERS, timeout=5, allow_redirects=True)
        if response.status_code in [200, 206, 301, 302]:
            return True
        response = requests.get(link, headers=HEADERS, timeout=5, stream=True)
        return response.status_code in [200, 206]
    except Exception:
        return False

def main():
    print(f"[{datetime.now()}] IPTV Auto-Healing & Logo Mapping Started...")
    
    all_channels = parse_m3u('active.m3u') + parse_m3u('dead.m3u')
    unique_channels = {c['link']: c['info'] for c in all_channels}
    
    active_list = []
    dead_list = []
    
    print(f"Total unique channels to check: {len(unique_channels)}")
    
    for link, info in unique_channels.items():
        is_alive = check_stream(link)
        
        if is_alive:
            # 🟢 လိုင်းကောင်းလျှင် Logo ရှာပြီး Auto တွဲပေးမည်
            logo_url = get_matched_logo(info)
            if logo_url:
                info = inject_logo(info, logo_url)
                print(f"🟢 ALIVE & Logo Mapped: {link[:40]}...")
            else:
                print(f"🟢 ALIVE (No Logo) for: {link[:40]}...")
            active_list.append((info, link))
        else:
            print(f"🔴 DEAD: {link[:40]}...")
            dead_list.append((info, link))
            
    with open('active.m3u', 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for info, link in active_list:
            f.write(f"{info}\n{link}\n")
            
    with open('dead.m3u', 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for info, link in dead_list:
            f.write(f"{info}\n{link}\n")

    print(f"Process Finished. Active: {len(active_list)} | Dead: {len(dead_list)}")

if __name__ == "__main__":
    main()
