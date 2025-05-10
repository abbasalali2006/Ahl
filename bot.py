from telegram import Update, ChatPermissions, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"أهلاً بك يا {update.effective_user.first_name}!")

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "الأوامر المتاحة:\n"
        "/start - ترحيب\n"
        "/help - المساعدة\n"
        "/protect - تفعيل حماية المجموعة\n"
        "/كتم - كتم عضو (رد على رسالة)\n"
        "/الغاء_الكتم - إلغاء الكتم (رد على رسالة)\n"
        "/طرد_الكل - طرد كل الأعضاء (المالك فقط)\n"
        "/تفليش - كتم جميع الأعضاء غير المشرفين"
    )

# /protect
async def protect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ['group', 'supergroup']:
        return await update.message.reply_text("هذا الأمر مخصص للمجموعات فقط.")

    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if member.status in ['administrator', 'creator']:
        await update.message.reply_text("تم تفعيل حماية المجموعة.")
    else:
        await update.message.reply_text("هذا الأمر مخصص للمشرفين فقط.")

# /كتم
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ['group', 'supergroup']:
        return await update.message.reply_text("يُستخدم هذا الأمر فقط في المجموعات.")

    admin = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if admin.status not in ['administrator', 'creator']:
        return await update.message.reply_text("فقط المشرفين يمكنهم استخدام هذا الأمر.")

    if not update.message.reply_to_message:
        return await update.message.reply_text("يرجى الرد على رسالة العضو الذي تريد كتمه.")

    user_to_mute = update.message.reply_to_message.from_user.id
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user_to_mute,
        permissions=ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text("تم كتم العضو بنجاح.")

# /الغاء_الكتم
async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ['group', 'supergroup']:
        return await update.message.reply_text("يُستخدم هذا الأمر فقط في المجموعات.")

    admin = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if admin.status not in ['administrator', 'creator']:
        return await update.message.reply_text("فقط المشرفين يمكنهم استخدام هذا الأمر.")

    if not update.message.reply_to_message:
        return await update.message.reply_text("يرجى الرد على رسالة العضو لإلغاء كتمه.")

    user_to_unmute = update.message.reply_to_message.from_user.id
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user_to_unmute,
        permissions=ChatPermissions(can_send_messages=True)
    )
    await update.message.reply_text("تم إلغاء الكتم عن العضو.")

# /طرد_الكل
async def kick_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    sender = await context.bot.get_chat_member(chat_id, user_id)
    if sender.status != 'creator':
        return await update.message.reply_text("فقط مالك المجموعة يمكنه تنفيذ هذا الأمر.")

    await update.message.reply_text("جارٍ طرد كل الأعضاء غير المشرفين...")

    admins = await context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admins]

    async for member in context.bot.get_chat_members(chat_id):
        if member.user.id not in admin_ids and not member.user.is_bot:
            try:
                await context.bot.ban_chat_member(chat_id, member.user.id)
            except:
                continue

    await update.message.reply_text("تم طرد جميع الأعضاء غير المشرفين.")

# /تفليش
async def flash_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    sender = await context.bot.get_chat_member(chat_id, user_id)
    if sender.status not in ['administrator', 'creator']:
        return await update.message.reply_text("فقط المشرفين يمكنهم تنفيذ هذا الأمر.")

    await update.message.reply_text("جارٍ تفليش المجموعة... (كتم جميع الأعضاء غير المشرفين)")

    admins = await context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admins]

    async for member in context.bot.get_chat_members(chat_id):
        if member.user.id not in admin_ids and not member.user.is_bot:
            try:
                await context.bot.restrict_chat_member(
                    chat_id,
                    member.user.id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
            except:
                continue

    await update.message.reply_text("تم كتم جميع الأعضاء غير المشرفين.")

# تشغيل البوت
if __name__ == '__main__':
    import os

    TOKEN = os.getenv("BOT_TOKEN", "7886210562:AAE8ddLrFy4X7nxvH1tPj1wW4PzjSLYnKeI")  # أو ضع التوكن مباشرة كسلسلة نصية

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("protect", protect_command))
    app.add_handler(CommandHandler("كتم", mute_user))
    app.add_handler(CommandHandler("الغاء_الكتم", unmute_user))
    app.add_handler(CommandHandler("طرد_الكل", kick_all))
    app.add_handler(CommandHandler("تفليش", flash_group))

    print("البوت يعمل...")
    app.run_polling()
