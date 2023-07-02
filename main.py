import asyncio
import glob
import os.path
from pydantic import BaseSettings
import aiofiles
import vk_api
import aiohttp
from os.path import getsize


class Settings(BaseSettings):
	TOKEN: str
	WALLPOST: bool
	GROUP_ID: int
	DESCRIPTION: str
	PUBLISH_DATE: str

	class Config:
		env_file = 'settings.env'
		env_file_encoding = 'utf-8'


settings = Settings()
vk_session = vk_api.VkApi(token=settings.TOKEN)
vk = vk_session.get_api()


def get_files():
	return glob.glob("videos/*")


async def upload(filename: str):
	description = input(f"Описание для {filename}: ")
	if settings.GROUP_ID == 0:
		a = vk.shortVideo.create(
			wallpost=int(settings.WALLPOST),
			file_size=getsize(f"videos/{filename}"),
			description=settings.DESCRIPTION,
			publish_date=settings.PUBLISH_DATE
		)
	else:
		a = vk.shortVideo.create(
			wallpost=int(settings.WALLPOST),
			file_size=getsize(f"videos/{filename}"),
			description=settings.DESCRIPTION,
			group_id=settings.GROUP_ID,
			publish_date=settings.PUBLISH_DATE
		)
	upload_url = a["upload_url"]

	async with aiofiles.open(f"videos/{filename}", "rb") as f:
		data = {"file": await f.read()}

	async with aiohttp.ClientSession() as session:
		async with session.post(
				upload_url,
				data=data,
		) as res:
			if res.status == 200:
				print(f"Загружен клип: {filename}")
			else:
				print(await res.text())
				print(f"Не удалось загрузить клип {filename}")


async def main():
	for file in get_files():
		filename = os.path.basename(file)
		await upload(filename)


if __name__ == "__main__":
	asyncio.run(main())
