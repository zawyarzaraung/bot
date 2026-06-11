import re

def check_football_smart(info_line):
    """ဘောလုံးနှင့် အားကစားလိုင်းများကို အမှိုက်မပါဘဲ စမတ်ကျကျ စစ်ထုတ်ရန်"""
    info_lower = info_line.lower()
    
    # ၁။ ဖယ်ထုတ်ရမည့် သတင်း၊ ဘာသာရေးနှင့် အထွေထွေ အမှိုက်စာလုံးများ (Strict Exclude)
    EXCLUDE_KEYWORDS = [
        'news', 'religious', 'muslim', 'quran', 'church', 'kids', 'cartoons', 
        'movie', 'music', 'radio', 'fashion', 'weather', 'cooking', 'brno',
        'subtitles', 'entertainment', 'documentary', 'educational'
    ]
    if any(ex in info_lower for ex in EXCLUDE_KEYWORDS):
        return False

    # ၂။ လက်ခံမည့် အားကစားနှင့် ဘောလုံးပွဲ သော့ချက်စာလုံးများ
    # (စာလုံးတွဲနေပါစေ - ဥပမာ beinsports1, truesport2 ဆိုလည်း အော်တိုမိစေရမယ်)
    SPORT_KEYWORDS = [
        'sport', 'futbol', 'football', 'soccer', 'fifa', 'premier', 'liga', 
        'bein', 'dazn', 'espn', 'fox', 'tudn', 'tsn', 'supersport', 'arena', 
        'sky', 'euro', 'match', 'clube', 'afc', 'uefa', 'cric', 'willow', 
        't sports', 'true', 'astro', 'sony', 'ten', 'star sports', 'fanatiz'
    ]
    
    # စာလုံး တစ်စိတ်တစ်ပိုင်း ပါဝင်ရုံဖြင့် သိမ်းဆည်းမည်
    return any(keyword in info_lower for keyword in SPORT_KEYWORDS)

def main():
    print("Reading M3U playlist for Smart Sports Filtering...")
    input_file = 'all_channels.m3u'
    output_file = 'active.m3u'
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found!")
        return

    matches = re.findall(r'(#EXTINF:.*?\n)(http.*?)(?=\n#EXTINF:|\n$|$)', content, re.DOTALL)
    
    selected_channels = []
    print(f"Total entries scanned from Big List: {len(matches)}")
    
    for info, link in matches:
        if check_football_smart(info):
            selected_channels.append((info.strip(), link.strip()))
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for info, link in selected_channels:
            f.write(f"{info}\n{link}\n")
            
    print(f"Successfully filtered {len(selected_channels)} Sports channels into {output_file}!")

if __name__ == "__main__":
    main()
