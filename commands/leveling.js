// commands/leveling.js
module.exports = (bot) => {
    bot.on('message', (ctx) => {
        const userId = ctx.from.id;
        if (!userData[userId]) return;
        
        userData[userId].exp += Math.floor(Math.random() * 10) + 1;
        if (userData[userId].exp >= userData[userId].level * 100) {
            userData[userId].level += 1;
            userData[userId].exp = 0;
            userData[userId].cash += 50;
            ctx.reply(`🎉 Selamat ${ctx.from.first_name}, kamu naik ke level ${userData[userId].level} dan mendapatkan 50 cash!`);
        }
        
        fs.writeFileSync('./data/userData.json', JSON.stringify(userData, null, 2));
    });
};