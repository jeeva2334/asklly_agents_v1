import asyncio
import time
from typing import List, Dict
from sqlalchemy.orm import Session
from text_to_speech import Speech
from utility import pretty_print
from router import AgentRouter
from speech_to_text import AudioTranscriber, AudioRecorder

class Interaction:
    def __init__(self, agents, tts_enabled: bool = True, stt_enabled: bool = True, recover_last_session: bool = False, langs: List[str] = ["en", "zh"]):
        self.is_active = True
        self.current_agent = None
        self.last_query = None
        self.last_answer = None
        self.last_reasoning = None
        self.agents = agents
        self.tts_enabled = tts_enabled
        self.stt_enabled = stt_enabled
        self.recover_last_session = recover_last_session
        self.router = AgentRouter(self.agents, supported_language=langs)
        self.ai_name = self._find_ai_name()
        self.speech = None
        self.transcriber = None
        self.recorder = None
        self.is_generating = False
        self.languages = langs
        self.bot_key = None
        self.browser_sources = None
        self.last_browser_search = None
        self.db: Session | None = None
        self.last_activity = time.time()

        if tts_enabled:
            self._initialize_tts()
        if stt_enabled:
            self._initialize_stt()
        if recover_last_session:
            self.load_last_session()
        self._emit_status()

    @property
    def browser(self):
        browser_agent = self.get_browser_agent()
        return browser_agent.browser if browser_agent else None

    def get_browser_agent(self):
        return next((agent for agent in self.agents if agent.type == "browser_agent"), None)

    def _find_ai_name(self) -> str:
        for agent in self.agents:
            if agent.type == "casual_agent":
                return agent.agent_name
        return "jarvis"

    def _initialize_tts(self):
        if not self.speech:
            self.speech = Speech(enable=self.tts_enabled, language=self.languages[0], voice_idx=1)

    def _initialize_stt(self):
        if not self.transcriber or not self.recorder:
            self.transcriber = AudioTranscriber(self.ai_name, verbose=False)
            self.recorder = AudioRecorder()

    def _emit_status(self):
        if self.stt_enabled:
            pretty_print(f"Text-to-speech trigger is {self.ai_name}", color="status")
        if self.tts_enabled:
            self.speech.speak("Hello, we are online and ready. What can I do for you?")
        pretty_print("asklly is ready.", color="status")

    def set_query(self, query: str, bot_key: str = None, db: Session = None) -> None:
        self.bot_key = bot_key
        self.is_active = True
        self.last_query = query
        self.db = db
        self.last_activity = time.time()

    async def think(self, uid, org) -> bool:
        if not self.last_query:
            return False

        self.last_activity = time.time()
        agent = await asyncio.to_thread(self.router.select_agent, self.last_query)

        if not agent:
            return False

        agent.set_org(org, uid)

        if self.current_agent != agent and self.last_answer:
            agent.memory.push('assistant', self.last_answer)

        self.current_agent = agent
        self.is_generating = True

        try:
            if agent.agent_name == "retrieval":
                self.last_answer, self.last_reasoning = await agent.process(self.last_query, bot_key=self.bot_key, db=self.db)
            else:
                self.last_answer, self.last_reasoning = await agent.process(self.last_query, self.speech)
        finally:
            self.is_generating = False

        return True
    
    async def close(self):
        if self.browser:
            await asyncio.to_thread(self.browser.driver.quit)

    def load_last_session(self):
        for agent in self.agents:
            if agent.type != "planner_agent":
                agent.memory.load_memory(agent.type)
