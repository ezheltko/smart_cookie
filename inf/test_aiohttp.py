import asyncio

import aiohttp


async def get_response(word_voice: str):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_voice}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                return None
            return await response.json()


if __name__ == '__main__':
    word = 'cake'
    res = asyncio.run(get_response(word))
    print(res[0].get('phonetics')[0]['audio'])
