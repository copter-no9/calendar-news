import os
import requests
from datetime import datetime
import pytz
import xml.etree.ElementTree as ET
import random
import time
import sys

def save_to_file(message, update_time, repo_name):
    """ฟังก์ชันสำหรับบันทึกข้อความลงไฟล์ index.html (หน้าเว็บ)"""
    actions_url = f"https://github.com/{repo_name}/actions/workflows/calendar_bot.yml"
    
    html_template = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Today's Market Watch</title>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Kanit', sans-serif;
            background-color: #f4f7f6;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
        }}
        .news-content {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            font-size: 16px;
            line-height: 1.6;
            white-space: pre-wrap;
            border: 1px solid #e9ecef;
            margin-bottom: 20px;
        }}
        .copy-btn {{
            width: 100%;
            padding: 15px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-family: 'Kanit', sans-serif;
            cursor: pointer;
            transition: background 0.3s;
            font-weight: 500;
        }}
        .copy-btn:hover {{
            background-color: #2980b9;
        }}
        .copy-btn.copied {{
            background-color: #2ecc71;
        }}
        .update-time {{
            text-align: center;
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        .update-btn {{
            display: block;
            width: 100%;
            padding: 12px;
            background-color: #f39c12;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-family: 'Kanit', sans-serif;
            cursor: pointer;
            transition: background 0.3s;
            text-align: center;
            text-decoration: none;
            margin-top: 15px;
            font-weight: 500;
            box-sizing: border-box;
        }}
        .update-btn:hover {{
            background-color: #d68910;
        }}
    </style>
</head>
<body>

    <div class="card">
        <div class="update-time">🕒 อัปเดตล่าสุด: {update_time}</div>
        <div class="news-content" id="newsText">{message}</div>

        <button class="copy-btn" id="copyBtn" onclick="copyText()">📋 กดคัดลอกข้อความ (Copy)</button>
        <a href="{actions_url}" target="_blank" class="update-btn">🔄 บังคับอัปเดตข้อมูลใหม่ (Manual Update)</a>
    </div>

    <script>
        function copyText() {{
            const textToCopy = document.getElementById('newsText').innerText;
            navigator.clipboard.writeText(textToCopy).then(() => {{
                const btn = document.getElementById('copyBtn');
                btn.innerText = '✅ คัดลอกเรียบร้อยแล้ว!';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.innerText = '📋 กดคัดลอกข้อความ (Copy)';
                    btn.classList.remove('copied');
                }}, 3000);
            }}).catch(err => {{
                console.error('Failed to copy: ', err);
                alert('ไม่สามารถคัดลอกได้อัตโนมัติ กรุณาคลุมดำแล้วก๊อปปี้เองครับ');
            }});
        }}
    </script>

</body>
</html>"""

    try:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_template)
        print("[+] บันทึกข้อความลงไฟล์ index.html สำเร็จ")
    except Exception as e:
        print(f"[-] เกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")


def get_economic_calendar():
    """ฟังก์ชันดึงข้อมูลปฏิทินเศรษฐกิจและคัดกรองข้อมูล"""
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
    
    # วนลูปเพื่อลองดึงข้อมูลใหม่ หากโดนแบน (Error 429) จะรอแล้วลองใหม่สูงสุด 5 ครั้ง
    max_retries = 5
    data = None
    
    for attempt in range(max_retries):
        try:
            # กำหนด timeout และเพิ่ม Headers เพื่อจำลองว่าเป็นเบราว์เซอร์จริงๆ
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # แปลงข้อมูล XML เป็น list ของ dictionary ให้เหมือน JSON เดิม
            root = ET.fromstring(response.content)
            data = []
            for event in root.findall('event'):
                item = {}
                for child in event:
                    item[child.tag] = child.text if child.text else ""
                data.append(item)
            
            # ถ้าดึงข้อมูลสำเร็จ ให้หลุดออกจากลูปทันที
            break
                
        except requests.exceptions.RequestException as e:
            print(f"[-] Error fetching data (Attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print("[*] กำลังรอ 30 วินาทีเพื่อลองดึงข้อมูลใหม่ (หลบการโดนบล็อก)...")
                time.sleep(30)
            else:
                print("[-] พยายามดึงข้อมูลจนครบโควต้าแล้ว แต่ยังไม่สำเร็จ")
                return None

    if data is None:
        return None

    # ข้อมูลจาก XML ของ ForexFactory (ผ่าน nfs) เวลาที่ได้มักจะเป็น UTC
    tz_utc = pytz.timezone('UTC')
    tz_bkk = pytz.timezone('Asia/Bangkok')
    
    # เวลาปัจจุบันในโซนไทย เพื่อเอาไว้เช็คว่าเป็น "วันนี้" หรือไม่
    now_bkk = datetime.now(tz_bkk)
    
    filtered_news = []
    
    for item in data:
        impact = item.get('impact', '')
        
        # 1. กรองเอาเฉพาะ High (แดง), Medium (ส้ม) และ Bank Holiday (เทา)
        if impact not in ['High', 'Medium', 'Holiday']:
            continue
            
        date_str = item.get('date', '') # เช่น "10-25-2023"
        time_str = item.get('time', '') # เช่น "8:30am", "All Day", "Tentative"
        country = item.get('country', '')
        title = item.get('title', '')
        
        is_exact_time = True
        news_datetime_bkk = None
        
        # 2. Edge Case: จัดการเวลา All Day / Tentative
        if time_str.lower() in ['all day', 'tentative'] or not time_str:
            is_exact_time = False
            time_str_to_parse = "12:00am" # สมมติเวลาเป็นเที่ยงคืน ET เพื่อใช้อ้างอิงวันที่
        else:
            time_str_to_parse = time_str
            
        try:
            # 3. Convert Timezone: แปลงจาก UTC ไปเป็นเวลาไทย (Asia/Bangkok)
            datetime_str_utc = f"{date_str} {time_str_to_parse.upper()}"
            dt_utc_unaware = datetime.strptime(datetime_str_utc, "%m-%d-%Y %I:%M%p")
            
            # ใส่ timezone UTC ให้ datetime object
            dt_utc_aware = tz_utc.localize(dt_utc_unaware)
            
            # แปลงเป็น timezone ไทย
            dt_bkk = dt_utc_aware.astimezone(tz_bkk)
            news_datetime_bkk = dt_bkk
            
        except ValueError as e:
            print(f"[-] พบปัญหาการแปลงเวลา (ข้ามข่าวนี้): {date_str} {time_str} -> {e}")
            continue

        # 4. Data Filtering: ตรวจสอบว่าเป็นข่าวของวันนี้ (ตามเวลาไทย) หรือไม่
        if news_datetime_bkk.date() != now_bkk.date():
            continue
            
        # 5. Formatting: จัด Emoji
        if impact == 'Holiday':
            filtered_news.append({
                'datetime': dt_bkk,
                'is_exact': False,
                'impact': impact,
                'country': country,
                'time_display': 'All Day',
                'emoji': '🏦'
            })
            continue

        if not is_exact_time:
            emoji = "📌"
            time_display = time_str.title()
        elif impact == 'High':
            emoji = "🔴"
            time_display = dt_bkk.strftime("%H:%M")
        else:
            emoji = "🟠"
            time_display = dt_bkk.strftime("%H:%M")
            
        filtered_news.append({
            'datetime': dt_bkk,
            'is_exact': is_exact_time,
            'impact': impact,
            'country': country,
            'time_display': time_display,
            'emoji': emoji
        })

    return filtered_news

def build_message(filtered_news):
    """สร้างข้อความแจ้งเตือนจากข้อมูลที่คัดกรองแล้ว"""
    if not filtered_news:
        return None
        
    # เรียงลำดับข่าวตามเวลาจากเช้าไปดึก
    filtered_news.sort(key=lambda x: x['datetime'])

    # สุ่มเลือกว่าจะใช้ฟอร์แมตไหน (1, 2, หรือ 3)
    format_choice = random.randint(1, 3)
    message_lines = []
    
    if format_choice == 1:
        message_lines.extend([
            "📊 อัปเดตตารางข่าวเศรษฐกิจประจำวัน ",
            "⚠️ ช่วงเวลาเฝ้าระวังความผันผวน ",
            "⚠️ คำแนะนำ: ควรหลีกเลี่ยงการเทรด",
            "ก่อนและหลังข่าว 15-30 นาที",
            ""
        ])
        
        for news in filtered_news:
            if news['impact'] == 'Holiday':
                message_lines.append(f"🏦 วันหยุดธนาคาร [{news['country']}]")
            else:
                message_lines.append(f"{news['emoji']} {news['time_display']} | [{news['country']}]")
                
        message_lines.extend([
            "",
            "🛡️ อย่าลืมวางแผนการเทรด",
            "และบริหารความเสี่ยงให้รัดกุมนะครับ ",
            "✅ ตั้ง TP / SL ทุกครั้ง",
            "เพื่อปกป้องพอร์ตของเราให้ปลอดภัย",
            "",
            "พอร์ตฟ้ากำไรปังๆ ทุกคนครับ 🚀 ",
            "— By Number9Option —",
            "",
            "🔗 อ้างอิงข้อมูลจาก: forexfactory"
        ])
        
    elif format_choice == 2:
        message_lines.extend([
            "🚨 Alert! 🚨เช็กข่าวก่อนลุยตลาดวันนี้ ",
            "ใครเทรดคู่ข้างล่างนี้ ระวังเวลาไว้เลย ",
            "กราฟมีโอกาสวิ่งแรง! ",
            "",
            "(ทริค: เลี่ยงชนข่าว 15-30 นาที ปลอดภัยสุดครับ)",
            "",
            "🔥 ข่าวแดง (ผันผวนสูง) ",
            "⚡ ข่าวส้ม (ผันผวนปานกลาง)",
            ""
        ])
        
        for news in filtered_news:
            if news['impact'] == 'Holiday':
                message_lines.append(f"🏦 วันหยุดธนาคาร [{news['country']}]")
            else:
                message_lines.append(f"{news['emoji']} {news['time_display']} ➔ [{news['country']}]")
                
        message_lines.extend([
            "",
            "จุดเข้าที่คม ต้องมาพร้อมกับวินัยที่เป๊ะ! ",
            "วางแผนแล้วอย่าลืมตั้ง TP / SL ",
            "ทุกไม้นะครับ ",
            "",
            "🛡️ เตรียมตัวให้พร้อม แล้วไปทำกำไรกัน 💸✨",
            "🎯 By Number9Option",
            "🔗 อ้างอิงข้อมูลจาก: forexfactory"
        ])
        
    elif format_choice == 3:
        message_lines.extend([
            "🗓️ Today's Market Watch ",
            "จับตาข่าววันนี้ 🗓️ ",
            "",
            "เช็กเวลาข่าวก่อนเทรด เพื่อลดความเสี่ยง",
            "จากกราฟกระชาก ‼️ ",
            "",
            "(เซฟพอร์ต: แนะนำงดเทรดช่วงข่าว 15-30 นาที)",
            ""
        ])
        
        for news in filtered_news:
            if news['impact'] == 'Holiday':
                message_lines.append(f"🏦 วันหยุดธนาคาร [{news['country']}]")
            else:
                message_lines.append(f"{news['emoji']} {news['time_display']} [{news['country']}]")
                
        message_lines.extend([
            "",
            "💡 Reminder: แผนการเทรดที่ดี ",
            "ต้องคุมความเสี่ยงได้ มีวินัย ตั้ง TP / SL ทุกครั้ง ",
            "",
            "💰 โชคดี มีกำไรครับ 💰 ",
            "© Number9Option",
            "🔗 อ้างอิงข้อมูลจาก: forexfactory"
        ])
    
    return "\n".join(message_lines)

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("[*] กำลังตรวจสอบปฏิทินเศรษฐกิจ...")
    
    news_data = get_economic_calendar()
    
    if news_data is None:
        print("[-] ไม่สามารถดึงข้อมูลได้ โปรแกรมสิ้นสุดการทำงานแบบติด Error เพื่อให้ GitHub แจ้งเตือน")
        sys.exit(1) # บังคับให้โปรแกรมจบแบบมี Error (เพื่อให้ GitHub Action ขึ้นกากบาทสีแดง)
    elif len(news_data) == 0:
        print("[-] วันนี้ไม่มีข่าวเศรษฐกิจสำคัญ (High/Medium)")
        final_message = "✅ วันนี้ตลาดปลอดโปร่ง\nไม่มีข่าวเศรษฐกิจสำคัญ (แดง/ส้ม) ให้ต้องระวังครับ\n\nสามารถเทรดตามเทคนิคได้อย่างเต็มที่เลยครับ 📈\n\nขอให้โชคดี มีกำไรครับ 💰\n© Number9Option"
        
        # ดึงเวลาปัจจุบันเพื่อโชว์บนหน้าเว็บ
        tz_bkk = pytz.timezone('Asia/Bangkok')
        current_time_str = datetime.now(tz_bkk).strftime("%d/%m/%Y %H:%M น.")
        repo_name = os.environ.get('GITHUB_REPOSITORY', 'username/repo')
        
        # อัปเดตหน้าเว็บเพื่อบอกว่าวันนี้ไม่มีข่าว
        save_to_file(final_message, current_time_str, repo_name)
    else:
        final_message = build_message(news_data)
        print("[+] สร้างข้อความสำเร็จ:\n")
        print(final_message)
        print("-" * 30)
        
        # ดึงเวลาปัจจุบันเพื่อโชว์บนหน้าเว็บ
        tz_bkk = pytz.timezone('Asia/Bangkok')
        current_time_str = datetime.now(tz_bkk).strftime("%d/%m/%Y %H:%M น.")
        
        # ดึงชื่อ Repository จาก GitHub Actions (ถ้าไม่มีให้ใช้ค่า Default)
        repo_name = os.environ.get('GITHUB_REPOSITORY', 'username/repo')
        
        # บันทึกลงไฟล์เพื่อให้ผู้ใช้อ่าน/ก๊อปปี้ผ่านเว็บ
        save_to_file(final_message, current_time_str, repo_name)
        
    print("[*] ทำงานเสร็จสิ้น")
