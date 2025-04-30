import sqlite3
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from mostaqel import M_scrape_jobs
from wuzzuf import W_scrape_jobs


token = "7282538675:AAG3H8xRjUb132jBAbpwASlfNRupX8UQRHk"

def categorize_jobs(site):
    db_file = 'MostaqelJobs.db' if site == "Mostaqel" else 'job.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    if site == "Mostaqel":
        cursor.execute("SELECT title, link, date, budget, skills FROM jobs ORDER BY date ASC")
        jobs = cursor.fetchall()
    else:
        cursor.execute("SELECT Title, Job_Link, Posted_Date, Company, Skills FROM jobs ORDER BY Posted_Date ASC")
        jobs = cursor.fetchall()

    conn.close()

    job_data = {
        "Data Science": [],
        "Mobile": [],
        "AI": [],
        "Frontend": [],
        "Backend": [],
        "Full Stack": [],
        "Other": []
    }

    for job in jobs:
        if site == "Mostaqel":
            title, link, date, budget, skills = job
            job_text = f"• title: {title}\n" \
                       f"• budget: {budget if budget else 'غير محدد'}\n" \
                       f"• date: {date if date else 'غير مذكور'}\n" \
                       f"• link: {link if len(link) <= 50 else link[:47] + '...'}"
        else:
            title, link, date, company, skills = job
            job_text = f"• title: {title}\n" \
                       f"• company: {company}\n" \
                       f"• date: {date if date else 'غير مذكور'}\n" \
                       f"• link: {link if len(link) <= 50 else link[:47] + '...'}"

        combined_text = f"{title} {skills}".lower() if skills else title.lower()

        if any(word in combined_text for word in ["full stack", "فل ستاك", "مطور شامل", "fullstack"]):
            job_data["Full Stack"].append(job_text)
        elif any(word in combined_text for word in ["flutter", "برمجة أندرويد", "اندرويد", "آيفون", "موبايل", "تطبيقات جوال", "ios", "android", "mobile", "react native", "كوتلن", "kotlin", "swift"]):
            job_data["Mobile"].append(job_text)
        elif any(word in combined_text for word in ["react", "فرونت اند", "تصميم واجهات", "واجهة المستخدم", "frontend", "html", "css", "javascript", "figma", "ui", "ux", "angular", "next.js", "svelte", "bootstrap", "tailwind"]):
            job_data["Frontend"].append(job_text)
        elif any(word in combined_text for word in ["node", "باك اند", "backend", "php", "لارافيل", "django", "دجانجو", "express", "api", "برمجة خلفية", "spring", "asp.net", "ruby on rails", "nestjs"]):
            job_data["Backend"].append(job_text)
        elif any(word in combined_text for word in ["ai", "ذكاء اصطناعي", "ذكاء صناعي", "machine learning", "deep learning", "neural networks", "الرؤية الحاسوبية", "nlp"]):
            job_data["AI"].append(job_text)
        elif any(word in combined_text for word in ["data", "تحليل البيانات", "تحليل بيانات", "تحليل", "data analysis", "data analyst", "pandas", "numpy", "statistics", "بيانات", "scikit-learn", "power bi", "sql", "excel"]):
            job_data["Data Science"].append(job_text)
        else:
            job_data["Other"].append(job_text)


    return job_data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Mostaqel"), KeyboardButton("Wuzzuf")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "اضغط هنا /start \nواختر الموقع الذي تريده 👇",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    valid_Web = ["Mostaqel", "Wuzzuf"]
    valid_choices = ["Frontend", "Backend", "Mobile", "AI", "Full Stack", "Data Science", "🔄 تحديث الوظائف","الرجوع", "Other"]

    if user_input in valid_Web:
        context.user_data["site"] = user_input

        keyboard = [
            [KeyboardButton("Data Science"), KeyboardButton("AI"), KeyboardButton("Mobile")],
            [KeyboardButton("Frontend"), KeyboardButton("Backend"), KeyboardButton("Full Stack")],
            [KeyboardButton("Other")],
            [KeyboardButton("الرجوع"),KeyboardButton("🔄 تحديث الوظائف")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "اختار المجال اللي مهتم بيه من الكيبورد تحت 👇",
            reply_markup=reply_markup
        )
        return
    
    if user_input == "الرجوع":
        keyboard = [
            [KeyboardButton("Mostaqel"), KeyboardButton("Wuzzuf")]
            ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "اختر الموقع من جديد 👇",
            reply_markup=reply_markup
            )
        return

    if "site" not in context.user_data:
        await update.message.reply_text("اضغط هنا /start \nواختر الموقع الذي تريده 👇")
        return

    site = context.user_data["site"]

    if user_input == "🔄 تحديث الوظائف":
        await update.message.reply_text("⏳ جاري تحديث الوظائف، انتظر لحظة...")
        try:
            if site == "Mostaqel":
                M_scrape_jobs("برمجة")
            else:
                W_scrape_jobs(["python", "Software Engineer"], 1)
            await update.message.reply_text("✅ تم تحديث الوظائف بنجاح!")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ أثناء التحديث: {e}")
        return

    if user_input not in valid_choices:
        await update.message.reply_text("❗/start من فضلك اختر خيارًا من الكيبورد.")
        return

    job_data = categorize_jobs(site)
    jobs = job_data.get(user_input, [])

    if jobs:
        for i in range(0, len(jobs), 5):
            response = f"الوظائف المتاحة في مجال {user_input}:\n\n" + "\n\n".join(jobs[i:i + 5])
            await update.message.reply_text(response)
    else:
        await update.message.reply_text(f"حالياً مفيش وظائف متاحة في مجال {user_input}.")
        
    


if __name__ == '__main__':
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
