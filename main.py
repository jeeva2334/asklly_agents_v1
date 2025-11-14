from logger import Logger
from dotenv import load_dotenv
import asyncio
from session_manager import SessionManager
load_dotenv()
logger = Logger("backend.log")
async def main():
    session_manager = SessionManager()
    cid = await session_manager.create_session()
    
    if not cid:
        logger.error("Failed to create a session.")
        return

    interaction = await session_manager.get_session(cid)

    from db import SessionLocal
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    session = next(get_db())

    try:
        interaction.set_query(query="Current dispute between thailand and combodia", bot_key="cx-odwb1gA9IRpgcVpk", db=session)
        print("Starting the questioning: Current dispute between thailand and combodia")
        await interaction.think("ffb76919-3348-53d4-b6f2-203e92277db2", "asklly")

        while True:
            await asyncio.sleep(1)
            if interaction.last_answer:
                print("Answer Generated")
                print("Reasoning: ", interaction.last_reasoning)
                print("Answer: ", interaction.last_answer)
                break
            print("Generating Answer....")

    finally:
        await session_manager.close_session(cid)

if __name__ == "__main__":
    asyncio.run(main())
