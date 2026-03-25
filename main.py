import pandas as pd
import unicodedata
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ====== CONFIG ======
TOKEN = "7545340925:AAHsKxNYcWeqa_8cQandlJDnAc6fAusBXbw"

# ====== HÀM XỬ LÝ TEXT ======
def remove_accents(text):
    text = str(text)

    # xử lý riêng chữ đ
    text = text.replace("đ", "d").replace("Đ", "D")

    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    return text.lower()

def clean_text(text):
    text = remove_accents(text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # bỏ ký tự đặc biệt
    return text

# ====== FORMAT ĐÁP ÁN ======
def get_correct_answers(row):
    answers = []
    try:
        correct_indexes = str(row["Correct"]).split(";")

        for i in correct_indexes:
            idx = int(i)
            answer_text = row[f"Answer{idx}"]
            answers.append(answer_text)
    except:
        pass

    return answers

# ====== LOAD DATA ======
df = pd.read_excel("data.xlsx")

# Normalize dữ liệu
df["normalized"] = df["Question Content"].apply(clean_text)

# ====== HÀM SEARCH ======
def search(keyword):
    keyword = clean_text(keyword)
    words = keyword.split()

    results = df.copy()

    for w in words:
        results = results[results["normalized"].str.contains(w, na=False)]

    return results.head(5)

# ====== HANDLE MESSAGE ======
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    results = search(text)

    if results.empty:
        await update.message.reply_text("❌ Không tìm thấy câu hỏi phù hợp")
        return

    msg = ""

    for _, row in results.iterrows():
        correct_answers = get_correct_answers(row)

        msg += f"📌 {row['Question Content']}\n"
        msg += "✅ Đáp án đúng:\n"

        for ans in correct_answers:
            msg += f"- {ans}\n"

        msg += "----------------------\n\n"

    await update.message.reply_text(msg)

# ====== MAIN ======
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🚀 Bot đang chạy...")
app.run_polling(close_loop=False)