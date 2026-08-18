from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import json
import os

# ===== KONFIGURASI =====
TOKEN = "8573133540:AAE8AFrP_i1VNt0b3MJkUpfhXU4RjYHIWN4"  
DAILY_LIMIT = 3
DATA_FILE = "noir_data.json"
CHANNEL_ID = "@MenfessNoirOfc"

# ===== LOAD DATA USER =====
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

# ===== FUNGSI CEK BATAS =====
def cek_batas(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    user_id_str = str(user_id)
    
    if user_id_str not in user_data or user_data[user_id_str]["date"] != today:
        user_data[user_id_str] = {"count": 0, "date": today}
        simpan_data()
    
    return user_data[user_id_str]["count"] < DAILY_LIMIT

def simpan_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f)

# ===== FUNGSI PARSE FORMAT MENFESS =====
def parse_menfess(text):
    lines = text.strip().split('\n')
    data = {
        'from': '',
        'to': '',
        'message': '',
        'songs': ''
    }
    
    current_key = None
    current_value = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.upper().startswith('MENFESS'):
            continue
            
        if '- From📥 :' in line or '- From :' in line:
            if current_key:
                data[current_key] = ' '.join(current_value).strip()
            current_key = 'from'
            current_value = [line.split(':', 1)[1].strip() if ':' in line else '']
        elif '- To📤 :' in line or '- To :' in line:
            if current_key:
                data[current_key] = ' '.join(current_value).strip()
            current_key = 'to'
            current_value = [line.split(':', 1)[1].strip() if ':' in line else '']
        elif '- Message✉️ :' in line or '- Message :' in line:
            if current_key:
                data[current_key] = ' '.join(current_value).strip()
            current_key = 'message'
            current_value = [line.split(':', 1)[1].strip() if ':' in line else '']
        elif '- Songs💿🎶 :' in line or '- Songs :' in line:
            if current_key:
                data[current_key] = ' '.join(current_value).strip()
            current_key = 'songs'
            current_value = [line.split(':', 1)[1].strip() if ':' in line else '']
        else:
            if current_key:
                current_value.append(line)
    
    if current_key:
        data[current_key] = ' '.join(current_value).strip()
    
    return data

# ===== HANDLER PERINTAH =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "Pengguna"
    
    pesan = f"""
Guysss!

Pernah ga sih kalian pengen ngomong sesuatu tapi bingung gimana?
Pengen kirim pesan sambil kasih rekomendasi lagu?
Ada yang mau ngomong tapi ga enak?
Atau mau ngirim kata-kata manis tapi malu?

Kirim lewat bot menfess ajaa, dijamin ke kirim secara anonim!

📝 Formatnya (klik teks di bawah untuk copy):

<code>MENFESS NOIR SOCIETY

- From📥 : 
- To📤 : 
- Message✉️ : 
- Songs💿🎶 :</code>

Setiap pesan bakal dipost di channel @MenfessNoirOfc

3x sehari, be nice ya guys gunakan bot dengan bijak.

/kuota - cek sisa
    """
    
    keyboard = [
        [InlineKeyboardButton("📝 Kirim Menfess", callback_data="format")],
        [InlineKeyboardButton("📊 Cek Kuota", callback_data="cek_kuota")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(pesan, parse_mode='HTML', reply_markup=reply_markup)

async def handle_menfess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if not text.upper().startswith('MENFESS'):
        await update.message.reply_text(
    "✖ Eh formatnya salah nih!\n\n"
    "Gunakan format:\n"
    "MENFESS NOIR SOCIETY\n"
    "- From📥 : \n"
    "- To📤 : \n"
    "- Message✉️ : \n"
    "- Songs💿🎶 : \n\n"
    "Ketik /start buat liat panduan lagi ya!",
    parse_mode='HTML'
)
        return
    
    data = parse_menfess(text)
    
    if not data['message']:
        await update.message.reply_text("❌ Pesan ga boleh kosong! Isi bagian Message✉️ ya!")
        return
    
    if not cek_batas(user_id):
        terpakai = user_data[str(user_id)]["count"]
        await update.message.reply_text(
            f"⚠️ Aduh! Batas hari ini udah habis!\n\n"
            f"Kamu udah kirim {terpakai} menfess hari ini.\n"
            f"Maksimal {DAILY_LIMIT} aja ya!\n\n"
            f"🔄 Besok lagi aja! Sabar ya 😁\n"
            f"🖤 Noir Society"
        )
        return
    
    try:
        from_text = data['from'] if data['from'] else 'Anonim'
        to_text = data['to'] if data['to'] else 'Semua'
        message_text = data['message']
        songs_text = data['songs'] if data['songs'] else 'Tanpa lagu'
        
        pesan_kirim = f"""
🖤 MENFESS NOIR SOCIETY 🖤
━━━━━━━━━━━━━━━━━━━━━━

📥 From : {from_text}
📤 To : {to_text}
✉️ Message : 
{message_text}
💿 Songs : {songs_text}

━━━━━━━━━━━━━━━━━━━━━━
🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━
🖤 @MenfessNoirOfc
        """
        
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=pesan_kirim,
            parse_mode='HTML'
        )
        
        user_data[str(user_id)]["count"] += 1
        sisa = DAILY_LIMIT - user_data[str(user_id)]["count"]
        simpan_data()
        
        await update.message.reply_text(
            f"✅ MANTAP! Menfess terkirim!\n\n"
            f"📥 From: {from_text}\n"
            f"📤 To: {to_text}\n"
            f"💿 Songs: {songs_text}\n\n"
            f"📊 Sisa kuota hari ini: {sisa}/{DAILY_LIMIT}\n\n"
            f"🖤 Noir Society\n"
            f"📢 Cek di @MenfessNoirOfc"
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Gagal ngirim nih!\n"
            f"Error: {str(e)}\n\n"
            f"Hubungi admin ya!"
        )

async def cek_kuota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today = datetime.now().strftime("%Y-%m-%d")
    user_id_str = str(user_id)
    
    if user_id_str not in user_data or user_data[user_id_str]["date"] != today:
        terpakai = 0
        sisa = DAILY_LIMIT
        status = "💚 Belom pake nih, gas aja!"
    else:
        terpakai = user_data[user_id_str]["count"]
        sisa = DAILY_LIMIT - terpakai
        if sisa > 0:
            status = "💚 Masih bisa kirim!"
        else:
            status = "🔴 Udah abis bos! Besok lagi ya 😁"
    
    pesan = f"""
📊 KUOTA MENFESS
━━━━━━━━━━━━━━━

📅 Hari ini: {today}
━━━━━━━━━━━━━━━
✅ Udah kepake: {terpakai}
⏳ Sisa: {sisa}
📌 Max: {DAILY_LIMIT}/hari
━━━━━━━━━━━━━━━
Status: {status}

🖤 Noir Society
    """
    
    keyboard = [[InlineKeyboardButton("📝 Kirim Menfess", callback_data="format")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(pesan, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "cek_kuota":
        await cek_kuota(update, context)
    elif query.data == "format":
        await query.edit_message_text(
            "📝 FORMAT MENFESS\n\n"
            "Copy dan isi ini ya!\n\n"
            "MENFESS NOIR SOCIETY\n\n"
            "- From📥 : Nama kamu\n"
            "- To📤 : Nama penerima\n"
            "- Message✉️ : Isi pesan\n"
            "- Songs💿🎶 : Judul lagu\n\n"
            "⚠️ INGET YA!\n"
            "• Message wajib diisi!\n"
            "• Max 3x sehari!\n"
            "• Kirim ke @MenfessNoirOfc\n\n"
            "🖤 Noir Society",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Balik", callback_data="back")]
            ])
        )
    elif query.data == "back":
        await start(update, context)

# ===== MAIN =====
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kuota", cek_kuota))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menfess))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("="*50)
    print("🤖 BOT MENFESS NOIR SOCIETY")
    print(f"📊 Limit: {DAILY_LIMIT}/hari")
    print(f"📢 Channel: {CHANNEL_ID}")
    print("="*50)
    print("✅ BOT NYALA!")
    print("Tekan CTRL+C buat matiin")
    print("="*50)
    
    app.run_polling()

if __name__ == "__main__":
    main()
