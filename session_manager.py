import asyncio
import uuid
import time
from typing import Dict
from interaction import Interaction
from agents import CasualAgent, BrowserAgent, CoderAgent, FileAgent, PlannerAgent, ReterivalAgent
from browser import Browser, create_driver
from llm_provider import Provider
import configparser
import sys
import os
from logger import Logger

config = configparser.ConfigParser()
config.read('config.ini')
logger = Logger("session_manager.log")

def is_running_in_docker():
    """Detect if code is running inside a Docker container."""
    if os.path.exists('/.dockerenv'):
        return True
    try:
        with open('/proc/1/cgroup', 'r') as f:
            return 'docker' in f.read()
    except:
        pass
    return False

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Interaction] = {}
        self.lock = asyncio.Lock()

    async def create_session(self, cid: str = None) -> str:
        async with self.lock:
            if cid is None:
                cid = str(uuid.uuid4())

            stealth_mode = config.getboolean('BROWSER', 'stealth_mode')
            personality_folder = "jarvis" if config.getboolean('MAIN', 'jarvis_personality') else "base"
            languages = config["MAIN"]["languages"].split(' ')

            headless = config.getboolean('BROWSER', 'headless_browser')
            if is_running_in_docker() and not headless:
                logger.warning("Detected Docker environment - forcing headless_browser=True")
                headless = True

            provider = Provider(
                provider_name=config["MAIN"]["provider_name"],
                model=config["MAIN"]["provider_model"],
                server_address=config["MAIN"]["provider_server_address"],
                is_local=config.getboolean('MAIN', 'is_local')
            )

            import random
            port = random.randint(10000, 65535)
            try:
                browser = Browser(
                    await asyncio.to_thread(create_driver, headless=headless, stealth_mode=stealth_mode, lang=languages[0], port=port),
                    anticaptcha_manual_install=stealth_mode
                )
            except Exception as e:
                logger.error(f"Failed to create browser for session {cid}: {e}")
                return None

            agents = [
                CasualAgent(
                    name=config["MAIN"]["agent_name"],
                    prompt_path=f"prompts/{personality_folder}/casual_agent.txt",
                    provider=provider, verbose=False, cid=cid
                ),
                CoderAgent(
                    name="coder",
                    prompt_path=f"prompts/{personality_folder}/coder_agent.txt",
                    provider=provider, verbose=False, cid=cid
                ),
                ReterivalAgent(
                    name="retrieval",
                    prompt_path=f"prompts/{personality_folder}/retrival_agent.txt",
                    provider=provider, verbose=False, cid=cid
                ),
                BrowserAgent(
                    name="Browser",
                    prompt_path=f"prompts/{personality_folder}/browser_agent.txt",
                    provider=provider, verbose=False, browser=browser, cid=cid
                ),
                PlannerAgent(
                    name="Planner",
                    prompt_path=f"prompts/{personality_folder}/planner_agent.txt",
                    provider=provider, verbose=False, browser=browser, cid=cid
                )
            ]

            interaction = Interaction(
                agents,
                tts_enabled=config.getboolean('MAIN', 'speak'),
                stt_enabled=config.getboolean('MAIN', 'listen'),
                recover_last_session=config.getboolean('MAIN', 'recover_last_session'),
                langs=languages
            )

            self.sessions[cid] = interaction
            logger.info(f"Created session {cid}")
            return cid

    async def get_session(self, cid: str) -> Interaction:
        async with self.lock:
            return self.sessions.get(cid)

    async def close_session(self, cid: str):
        async with self.lock:
            if cid in self.sessions:
                interaction = self.sessions.pop(cid)
                await interaction.close()
                logger.info(f"Closed session {cid}")

    async def cleanup_inactive_sessions(self, timeout: int = 3600):
        while True:
            await asyncio.sleep(timeout)
            async with self.lock:
                inactive_sessions = []
                for cid, interaction in self.sessions.items():
                    if (time.time() - interaction.last_activity) > timeout:
                        inactive_sessions.append(cid)

                for cid in inactive_sessions:
                    await self.close_session(cid)
