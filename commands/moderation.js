// commands/moderation.js
module.exports = (bot) => {
    bot.command('ban', (ctx) => {
        if (!ctx.message.reply_to_message) return ctx.reply('Balas pesan user yang ingin di-ban!');
        ctx.banChatMember(ctx.message.reply_to_message.from.id);
        ctx.reply('User telah di-ban!');
    });

    bot.command('unban', (ctx) => {
        const args = ctx.message.text.split(' ');
        if (args.length < 2) return ctx.reply('Gunakan format: /unban [user_id]');
        ctx.unbanChatMember(args[1]);
        ctx.reply('User telah di-unban!');
    });
};