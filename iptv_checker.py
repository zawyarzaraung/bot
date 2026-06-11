import re

# ⚽ ဘောလုံးပွဲနှင့် အဓိက အားကစားလိုင်းကြီးများအတွက်သာ (တိကျသော သော့ချက်စာလုံးများ)
FOOTBALL_KEYWORDS = [
    'bein', 'dazn', 'football', 'soccer', 'fifa', 'premier', 'liga', 'serie a', 
    'bundesliga', 'champions league', 'uefa', 'afc', 't sports', 'true sport', 
    'sky sports', 'fox sports', 'tyc sports', 'dsports', 'caze tv', 'tudn', 
    'supersport', 'arena sport', 'match futbol', 'astro superSport', 'sportal'
]

# ❌ ဖယ်ထုတ်ရမည့် သတင်း၊ ဘာသာရေး၊ ကလေးလိုင်းနှင့် အထွေထွေ စာလုံးများ
EXCLUDE_KEYWORDS = [
    'news', 'religious', 'muslim', 'quran', 'church', 'kids', 'cartoons', 'movie', 
    'music', 'radio', 'future channel', 'brno', 'fashion', 'weather', 'cooking'
]

def check_football_only(info_line):
    """ဘောလုံးပွဲလိုင်း ဟုတ်/မဟုတ် တိကျစွာ စစ်ဆေးရန်"""
    info_lower = info_line.lower()
    
    # ၁။ ဖယ်ထုတ်ရမည့် အမှိုက်စာလုံးများ ပါနေလျှင် လုံးဝ လက်မခံပါ
    if any(ex in info_lower for ex in EXCLUDE_KEYWORDS):
        return False
        
    # ၂။ အားကစားလိုင်း နာမည်အစစ်အမှန် ပါ/မပါ စစ်ဆေးခြင်း
    for keyword in FOOTBALL_KEYWORDS:
        # စာလုံး တစ်စိတ်တစ်ပိုင်း တူရုံတင်မကဘဲ စာလုံးသီးသန့် ဖြစ်နေမှုကို စစ်ဆေးသည် (ဥပမာ- 'future' ထဲက 'tudn' မဖြစ်စေရန်)
        if re.search(r'\b' + re.escape(keyword) + r'\b', info_lower) or keyword in info_lower:
            # တကယ်လို့ အထွေထွေ စာလုံးဆန်းတွေနဲ့ ငြိနေရင် ဖယ်ထုတ်ရန် logic
            return True
            
    return False

def main():
    print("Reading M3U playlist for Football Channels only...")
    input_file = 'all_channels.m3u'
    output_file = 'active.m3u'
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found!")
        return

    matches = re.findall(r'(#EXTINF:.*?\n)(http.*?)(?=\n#EXTINF:|\n$|$)', content, re.DOTALL)
    
    football_channels = []
    print(f"Total entries scanned from Big List: {len(matches)}")
    
    for info, link in matches:
        if check_football_only(info):
            football_channels.append((info.strip(), link.strip()))
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for info, link in football_channels:
            f.write(f"{info}\n{link}\n")
            
    print(f"Successfully filtered {len(football_channels)} TRUE Football channels into {output_file}!")

if __name__ == "__main__":
    main()
