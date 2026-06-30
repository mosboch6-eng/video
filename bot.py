import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# التوكن ديال البوت
BOT_TOKEN = "8212988137:AAHL1WUYULRQnSjbm9SFP1L1SZB0URqRw4Q"

# رابط القناة ديالك لي صاوبتي
CHANNEL_USERNAME = "@Movies_VIP_2026"

# الأيدي ديالك
ADMIN_ID = 7278050418

bot = telebot.TeleBot(BOT_TOKEN)

def save_user(user_id):
    try:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        users = []
    
    if str(user_id) not in users:
        with open("users.txt", "a") as f:
            f.write(f"{user_id}\n")

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.from_user.id)
    welcome_text = """
مرحباً بك في أفضل بوت لتحميل الفيديوهات! 🚀

أرسل لي رابط أي مقطع فيديو وسأقوم بتحميله لك فوراً بأعلى جودة وبدون علامة مائية (تيك توك، انستغرام، فيسبوك، يوتيوب...).
🔗 هيا، انسخ الرابط وأرسله لي الآن:
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['broadcast'])
def send_broadcast(message):
    if message.from_user.id == ADMIN_ID:
        text_to_send = message.text.replace('/broadcast', '').strip()
        if not text_to_send:
            bot.reply_to(message, "اكتب الرسالة بعد الأمر، مثلاً: /broadcast السلام عليكم")
            return
        
        try:
            with open("users.txt", "r") as f:
                users = f.read().splitlines()
        except FileNotFoundError:
            users = []
            
        success = 0
        for user in users:
            try:
                bot.send_message(user, text_to_send)
                success += 1
            except Exception:
                pass
        bot.reply_to(message, f"✅ تم إرسال الرسالة إلى {success} مستخدم.")
    else:
        bot.reply_to(message, "❌ ليس لديك صلاحية لاستخدام هذا الأمر.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    user_id = message.from_user.id
    url = message.text
    save_user(user_id)

    if not check_subscription(user_id):
        markup = InlineKeyboardMarkup()
        join_btn = InlineKeyboardButton(text="📢 اضغط هنا للاشتراك", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
        markup.add(join_btn)
        bot.send_message(message.chat.id, "⚠️ عذراً! لتتمكن من تحميل الفيديوهات، يجب عليك الاشتراك في قناتنا أولاً.", reply_markup=markup)
        return

    bot.reply_to(message, "⏳ جاري التحميل، يرجى الانتظار قليلاً...")
    ydl_opts = {'format': 'best', 'outtmpl': f'{user_id}_video.%(ext)s', 'quiet': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        ad_caption = """
✅ تم التحميل بنجاح!
---
🎁 ضاعف أموالك الآن! تسجل باستخدام كود الخصم PROMO200 واحصل على مكافأة 200% على إيداعك الأول.
        """
        with open(filename, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, caption=ad_caption)
        os.remove(filename) 

    except Exception as e:
        bot.reply_to(message, "❌ حدث خطأ أثناء التحميل! تأكد من أن الرابط صحيح.")

if __name__ == '__main__':
    bot.infinity_polling()

