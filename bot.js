// bot.js
const { Telegraf } = require('telegraf');
const fs = require('fs');
const config = require('./config.json');
const moderation = require('./commands/moderation');
const leveling = require('./commands/leveling');
const randomMessage = require('./commands/randomMessage');
const stickerMaker = require('./commands/stickerMaker');
const { exec } = require('child_process');

const bot = new Telegraf(config.token);

// Load Data
const welcomeData = JSON.parse(fs.readFileSync('./data/welcome.json', 'utf8'));
const userData = JSON.parse(fs.readFileSync('./data/userData.json', 'utf8'));
const randomMessages = [
    "Jangan lupa baca aturan grup!",
    "Tetap sopan dan hormat dalam diskusi!",
    "Ada yang butuh bantuan? Moderator siap membantu!",
    "Jangan spam ya! Mari jaga kenyamanan bersama."
];

function generateRandomId() {
    return Math.floor(100000 + Math.random() * 900000).toString();
}

bot.on('new_chat_members', (ctx) => {
    const user = ctx.message.new_chat_members[0];
    let userId;
    
    if (!userData[user.id]) {
        userId = generateRandomId();
        userData[user.id] = { randomId: userId, exp: 0, cash: 0, level: 1 };
    } else {
        userId = userData[user.id].randomId;
    }
    
    fs.writeFileSync('./data/userData.json', JSON.stringify(userData, null, 2));
    ctx.reply(`${welcomeData.welcomeMessage}\nID Kamu: ${userId}`);
});

bot.on('left_chat_member', (ctx) => {
    ctx.reply(welcomeData.exitMessage);
});

// Moderation Commands
moderation(bot);

// Leveling System
leveling(bot);

// Random Messages
randomMessage(bot);

// Sticker Maker
stickerMaker(bot);

bot.launch();
console.log('Bot is running!');