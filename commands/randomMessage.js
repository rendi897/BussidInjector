// commands/randomMessage.js
module.exports = (bot) => {
    function sendRandomMessage() {
        const chatId = config.group_id;
        const message = randomMessages[Math.floor(Math.random() * randomMessages.length)];
        bot.telegram.sendMessage(chatId, message);
        
        const nextInterval = Math.floor(Math.random() * (10 * 60 * 60 * 1000 - 30 * 60 * 1000)) + 30 * 60 * 1000;
        setTimeout(sendRandomMessage, nextInterval);
    }
    setTimeout(sendRandomMessage, Math.floor(Math.random() * (10 * 60 * 60 * 1000 - 30 * 60 * 1000)) + 30 * 60 * 1000);
};