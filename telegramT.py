from telegram import Bot
from telegram import Update
import asyncio

# 텔레그램 봇 설정
token = '7342119999:AAGDSoygl_OJxkTHORfUIX_2e_2IZ_XM6Gk'
id='7118641461'
    # 여기에 실제 토큰과 채팅방 아이디를 사용하여 인스턴스 생성 예시
    # 비동기 함수 정의
async def tele_send(msg):
    
    async with bot:
        #print(await bot.get_me())       
        #updates = await bot.getUpdates()
        #print(updates[0].message.chat_id)
        await bot.send_message(text=msg, chat_id=id)

def init_telegram() :
    global bot
    bot = Bot(token=token)

# 이벤트 루프 실행
if __name__ == "__main__":
    asyncio.run(main())