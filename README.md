# ข่าวภัยไซเบอร์ (Threat Watch)

รวบรวมข่าวภัยคุกคามทางไซเบอร์จากฟีด RSS แสดงผลเป็นเว็บแอปที่ใช้ได้ทั้งมือถือและคอมพิวเตอร์ และส่งแจ้งเตือนเข้า Telegram เมื่อพบข่าวที่ตรงกับคำสำคัญ

## ไฟล์ในโปรเจกต์

| ไฟล์ | หน้าที่ |
|---|---|
| `index.html` | หน้าเว็บแอป (เมนูบนซ้าย เมนูล่าง ตั้งค่าฟีดได้) |
| `feeds.json` | รายการฟีด RSS และคำสำคัญที่ใช้ส่งแจ้งเตือน |
| `fetch_news.py` | สคริปต์ดึงข่าว เขียน `news.json` และส่ง Telegram |
| `.github/workflows/news.yml` | ตั้งเวลาให้ GitHub Actions รันสคริปต์ทุก 30 นาที |
| `news.json`, `seen.json` | สร้างอัตโนมัติหลังรันครั้งแรก (ข่าวที่ดึงมา และรายการที่ส่งไปแล้ว) |

## วิธีติดตั้ง

1. อัปโหลดไฟล์ทั้งหมดเข้า repo (โฟลเดอร์ `.github` ต้องอยู่ที่ root ของ repo)
2. เปิด GitHub Pages: **Settings > Pages** เลือก Deploy from a branch, branch `main`, โฟลเดอร์ `/ (root)`
3. สร้าง Telegram bot ที่ `@BotFather` เพื่อรับ Bot Token และหา Chat ID ของคุณ
4. เพิ่ม secret ที่ **Settings > Secrets and variables > Actions**
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
5. เปิด **Settings > Actions > General** ตั้ง Workflow permissions เป็น **Read and write permissions**
6. ไปที่แท็บ **Actions** เลือก `fetch-news` แล้วกด **Run workflow** เพื่อทดสอบ

เมื่อรันเสร็จจะมี `news.json` ใน repo และแอปจะแสดงข่าวจริง

## การเพิ่มหรือลบฟีด

1. เปิดแอป ไปที่แท็บ **ตั้งค่า**
2. เพิ่มหรือลบฟีด และแก้คำสำคัญ
3. กด **คัดลอก** หรือ **ดาวน์โหลด** ไฟล์ `feeds.json`
4. นำไปวางทับ `feeds.json` ใน repo สคริปต์จะใช้ค่าใหม่ในรอบถัดไป

## หมายเหตุ

- การรันครั้งแรกจะไม่ส่ง Telegram เพื่อกันข้อความท่วม
- ระดับความรุนแรงของข่าวเดาจากคำในหัวข้อ เช่น zero-day, actively exploited, critical
- ถ้าใช้ repo private บนแผนฟรี GitHub Pages จะใช้ไม่ได้ และโควตา Actions ของ repo private มีจำกัด ควรลดความถี่ใน `news.yml` (เช่น `0 * * * *` เพื่อรันทุกชั่วโมง)
- อย่าใส่ Bot Token ในไฟล์ใน repo ให้เก็บใน Actions secrets เท่านั้น
