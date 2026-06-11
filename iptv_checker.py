import os
import requests
import re
from datetime import datetime

# Headers for checking streams (Avoid 403 Forbidden)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def parse_m3u(file_path):
    """M3U ဖိုင်ကို ဖတ်ပြီး Channel Info နဲ့ Link ကို ခွဲထုတ်ပေးသည့် Function"""
    channels = []
    if not os.path.exists(file_path):
        return channels
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # EXTINF tag နှင့် Link များကို ရှာဖွေခြင်း
    matches = re.findall(r'(#EXTINF:.*?\n)(http.*?)(?=\n#EXTINF:|\n$|$)', content, re.DOTALL)
    for info, link in matches:
        channels.append({
            'info': info.strip(),
            'link': link.strip()
        })
    return channels

def check_stream(link):
    """Stream Link အလုပ်လုပ်မလုပ် စစ်ဆေးခြင်း"""
    try:
        # Stream ကို အဆုံးထိ ဒေါင်းမနေစေရန် stream=True ထားပြီး Header သာ စစ်မည်
        response = requests.head(link, headers=HEADERS, timeout=5, allow_redirects=True)
        if response.status_code in [200, 206, 301, 302]:
            return True
        # Head Request ကို ပိတ်ထားပါက GET ဖြင့် ထပ်စစ်မည်
        response = requests.get(link, headers=HEADERS, timeout=5, stream=True)
        return response.status_code in [200, 206]
    except Exception:
        return False

def main():
    print(f"[{datetime.now()}] IPTV Auto-Healing Process Started...")
    
    # ဖိုင်အဟောင်းများမှ လိုင်းများအားလုံးကို စုစည်းခြင်း
    all_channels = parse_m3u('active.m3u') + parse_m3u('dead.m3u')
    
    # Duplicate (လိုင်းထပ်နေတာများ) ရှိပါက ဖယ်ထုတ်ခြင်း
    unique_channels = {c['link']: c['info'] for c in all_channels}
    
    active_list = []
    dead_list = []
    
    print(f"Total unique channels to check: {len(unique_channels)}")
    
    for link, info in unique_channels.items():
        print(f"Checking: {link[:50]}... ", end="")
        is_alive = check_stream(link)
        
        if is_alive:
            print("🟢 ALIVE")
            active_list.append((info, link))
        else:
            print("🔴 DEAD")
            dead_list.append((info, link))
            
    # active.m3u အသစ်ပြန်ရေးသားခြင်း
    with open('active.m3u', 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for info, link in active_list:
            f.write(f"{info}\n{link}\n")
            
    # dead.m3u အသစ်ပြန်ရေးသားခြင်း
    with open('dead.m3u', 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for info, link in dead_list:
            f.write(f"{info}\n{link}\n")

    print(f"Process Finished. Active: {len(active_list)} | Dead: {len(dead_list)}")

if __name__ == "__main__":
    main()
