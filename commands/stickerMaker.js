// commands/stickerMaker.js
module.exports = (bot) => {
    bot.on('photo', async (ctx) => {
        const fileId = ctx.message.photo.pop().file_id;
        const fileLink = await ctx.telegram.getFileLink(fileId);
        const outputFilePath = `./sticker_${ctx.from.id}.webp`;
        
        exec(`wget -O input.jpg "${fileLink}" && convert input.jpg -resize 512x512 ${outputFilePath}`, async (error) => {
            if (error) return ctx.reply('❌ Gagal mengonversi gambar ke stiker.');
            await ctx.replyWithSticker({ source: outputFilePath });
            fs.unlinkSync(outputFilePath);
        });
    });
};