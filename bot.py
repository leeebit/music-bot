import logging
import asyncio
from webbrowser import get
from aiogram import Bot, Dispatcher, types 
from aiogram.filters import Command 
from aiogram.types import FSInputFile
import yt_dlp
import os
import time

logging.basicConfig(level=logging.INFO)

bot = Bot(token="6408238757:AAHNs9ApmYEnz0uELWMMmth7nUtLuwXkgt0")
dp = Dispatcher()

class FilenameCollectorPP(yt_dlp.postprocessor.common.PostProcessor):
	def __init__(self):
		super(FilenameCollectorPP, self).__init__(None)
		self.filenames = []

	def run(self, information):
		self.filenames.append(information["filepath"])
		return [], information

@dp.message(lambda message: not message.text.startswith('/'))
async def unknown_command(message: types.Message):
    await message.reply("Извините, не отправляйте мне то чего я не знаю, я ломаюсь (. \n Ознакомьтесь с руководством пользователя при помощи команды /help")

@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    nickname = message.from_user.username
    if nickname:
        await message.reply(f"Hey, {nickname}!")
    else:
        await message.reply("Hey!")

@dp.message(Command('help'))
async def send_instructions(message: types.Message):
    instructions = "Руководство пользователя:\n🟢все запросы вводятся в одну строчку ОБЯЗАТЕЛЬНО с названием команды, например:\n/sea *исполнитель - название*\n/yt *ссылка на песню ТОЛЬКО на ютуб*\n🟢Если запрос будет введен разными сообщения (команда одно сообщение, песня - другим), то бот не сработает!\n🔴При нажатии на кнопку меню ВАЖНО удерживать команду, тогда она введется в поисковую строку, а не просто отправится🔴"
    await message.reply(instructions)

@dp.message(Command('sea'))
async def search(message: types.Message):
	arg = message.text.split(maxsplit=1)[1]
	await message.reply('Ожидайте...')
	YDL_OPTIONS = {'format': 'bestaudio/best',
		'noplaylist':'True',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192'
		}],
	}
	with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
		try:
			get(arg) 
		except:
			filename_collector = FilenameCollectorPP()
			ydl.add_post_processor(filename_collector)
			video = ydl.extract_info(f"ytsearch:{arg}", download=True)['entries'][0]
			await message.reply_document(FSInputFile(filename_collector.filenames[0]))
			await message.reply(f'Файл был отправлен!\nСпасибо за использование бота\n\n__{arg}__')
			time.sleep(5)
			os.remove(filename_collector.filenames[0])
			
		else:
			video = ydl.extract_info(arg, download=True)
		
		return filename_collector.filenames[0]

@dp.message(Command('yt'))
async def youtube(message: types.Message):
	arguments = message.text.split(maxsplit=1)[1]
	await message.reply("Ожидайте...")
	ydl_opts = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
	}
	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		filename_collector = FilenameCollectorPP()
		ydl.add_post_processor(filename_collector)
		ydl.download([arguments])
		
		
		await message.reply_document(FSInputFile(filename_collector.filenames[0]))
		await message.reply(f'Файл был отправлен!\nСпасибо за использование бота\n\n__{arguments}__')
		time.sleep(5)
		os.remove(filename_collector.filenames[0])
		return filename_collector.filenames[0]

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

