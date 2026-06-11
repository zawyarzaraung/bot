import re

# ⚽ ရှာဖွေမည့် အားကစားနှင့် ဘောလုံးပွဲဆိုင်ရာ သော့ချက်စာလုံးများ (Keywords)
SPORTS_KEYWORDS = [
    'sport', 'football', 'soccer', 'fifa', 'bein', 'dazn', 'espn', 'fox', 
    'cricket', 'tUDN', 'tsn', 'supersport', 'arena', 'sky', 'euro', 'tvc', 
    'liga', 'premier', 'match', 'clube', 'afc', 'uefa', 'cric'
]

def check_sports(text):
    """စာသားထဲတွင် အားကစားသတ်မှတ်ချက် ပါ/မပါ စစ်ဆေးရန်"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SPORTS_KEYWORDS)

def main():
    print("Reading huge M3U playlist file...")
    
    # ⚠️ မင်းရဲ့ လိုင်း ၁၅,၀၀၀ ပါတဲ့ ဖိုင်နာမည်ကို 'all_channels.m3u' ဟု ပြောင်းလဲသတ်မှတ်ထားသည်
    input_file = 'all_channels.m3u' 
    output_file = 'active.m3u'
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found! Please upload your 15,000 channels file as '{input_file}' first.")
        return

    # EXTINF နှင့် လင့်ခ် အတွဲများကို ရှာဖွေခြင်း
    matches = re.findall(r'(#EXTINF:.*?\n)(http.*?)(?=\n#EXTINF:|\n$|$)', content, re.DOTALL)
    
    sports_channels = []
    print(f"Total lines scanned: {len(matches)}")
    
    for info, link in matches:
        # EXTINF line သို့မဟုတ် လိုင်းနာမည်ထဲတွင် အားကစား Keyword ပါလျှင် သိမ်းဆည်းမည်
        if check_sports(info):
            sports_channels.append((info.strip(), link.strip()))
            
    # ရလာတဲ့ ဘောလုံးလိုင်းများကို active.m3u ထဲသို့ ရေးထည့်ခြင်း
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for info, link in sports_channels:
            f.write(f"{info}\n{link}\n")
            
    print(f"Successfully extracted {len(sports_channels)} sports channels into {output_file}!")

if __name__ == "__main__":
    main()
