import datetime
import uuid
import torch, config
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from pymongo import MongoClient

from utility import pretty_print, animate_thinking
from logger import Logger

class Memory():
    """
    Memory is a class for managing the conversation memory
    It provides a method to compress the memory using summarization model.
    """
    def __init__(self, system_prompt: str,
                 cid: str = None,
                 memory_compression: bool = True,
                 model_provider: str = "deepseek-r1:14b"):
        self.memory = [{'role': 'system', 'content': system_prompt}]
        self.logger = Logger("memory.log")
        
        # MongoDB setup
        mongo_uri = config.MONGO_URI
        mongo_db_name = config.MONGO_DB_NAME
        mongo_collection_name = "agents_chat"
        self.client = MongoClient(mongo_uri)
        self.db = self.client[mongo_db_name]
        self.collection = self.db[mongo_collection_name]
        
        self.cid = cid if cid else str(uuid.uuid4())
        self.load_memory()
        # memory compression system
        self.model = None
        self.tokenizer = None
        self.device = self.get_cuda_device()
        self.memory_compression = memory_compression
        self.model_provider = model_provider
        if self.memory_compression:
            self.download_model()

    def get_ideal_ctx(self, model_name: str) -> int | None:
        """
        Estimate context size based on the model name.
        EXPERIMENTAL for memory compression
        """
        import re
        import math

        def extract_number_before_b(sentence: str) -> int:
            match = re.search(r'(\d+)b', sentence, re.IGNORECASE)
            return int(match.group(1)) if match else None

        model_size = extract_number_before_b(model_name)
        if not model_size:
            return None
        base_size = 7  # Base model size in billions
        base_context = 4096  # Base context size in tokens
        scaling_factor = 1.5  # Approximate scaling factor for context size growth
        context_size = int(base_context * (model_size / base_size) ** scaling_factor)
        context_size = 2 ** round(math.log2(context_size))
        self.logger.info(f"Estimated context size for {model_name}: {context_size} tokens.")
        return context_size
    
    def download_model(self):
        """Download the model if not already downloaded."""
        animate_thinking("Loading memory compression model...", color="status")
        self.tokenizer = AutoTokenizer.from_pretrained("pszemraj/led-base-book-summary")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("pszemraj/led-base-book-summary")
        self.logger.info("Memory compression system initialized.")
    
    def save_memory(self) -> None:
        """Save the session memory to MongoDB."""
        self.collection.update_one(
            {'cid': self.cid},
            {'$set': {
                'memory': self.memory,
                'model_provider': self.model_provider,
                'last_update': datetime.datetime.now()
            }},
            upsert=True
        )
        self.logger.info(f"Saved memory for cid {self.cid}")

    def load_memory(self) -> None:
        """Load the memory from MongoDB."""
        pretty_print(f"Loading past memories for cid {self.cid}... ", color="status")
        session_data = self.collection.find_one({'cid': self.cid})
        if session_data and 'memory' in session_data:
            self.memory = session_data['memory']
            self.model_provider = session_data.get('model_provider', self.model_provider)
            if self.memory and self.memory[-1]['role'] == 'user':
                self.memory.pop()
            self.compress()
            pretty_print("Session recovered successfully", color="success")
        else:
            pretty_print("No memory to load for this cid.", color="error")
    
    def reset(self, memory: list = []) -> None:
        self.logger.info("Memory reset performed.")
        self.memory = memory
    
    def push(self, role: str, content: str, context: str=None, query: str=None) -> int:
        """Push a message to the memory."""
        ideal_ctx = self.get_ideal_ctx(self.model_provider)
        if ideal_ctx is not None:
            if self.memory_compression and len(content) > ideal_ctx * 1.5:
                self.logger.info(f"Compressing memory: Content {len(content)} > {ideal_ctx} model context.")
                self.compress()
        curr_idx = len(self.memory)
        if self.memory[curr_idx-1]['content'] == content:
            pretty_print("Warning: same message have been pushed twice to memory", color="error")
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = {'role': role, 'content': content, 'time': time_str, 'model_used': self.model_provider}
        if context:
            message['context'] = context
        if query:
            message['query'] = query
        self.memory.append(message)
        self.save_memory()
        return curr_idx-1
    
    def clear(self) -> None:
        """Clear all memory except system prompt"""
        self.logger.info("Memory clear performed.")
        self.memory = self.memory[:1]
        self.save_memory()
    
    def clear_section(self, start: int, end: int) -> None:
        """
        Clear a section of the memory. Ignore system message index.
        Args:
            start (int): Starting bound of the section to clear.
            end (int): Ending bound of the section to clear.
        """
        self.logger.info(f"Clearing memory section {start} to {end}.")
        start = max(0, start) + 1
        end = min(end, len(self.memory)-1) + 2
        self.memory = self.memory[:start] + self.memory[end:]
        self.save_memory()
    
    def get(self) -> list:
        return self.memory

    def get_cuda_device(self) -> str:
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"

    def summarize(self, text: str, min_length: int = 64) -> str:
        """
        Summarize the text using the AI model.
        Args:
            text (str): The text to summarize
            min_length (int, optional): The minimum length of the summary. Defaults to 64.
        Returns:
            str: The summarized text
        """
        if self.tokenizer is None or self.model is None:
            self.logger.warning("No tokenizer or model to perform summarization.")
            return text
        if len(text) < min_length*1.5:
            return text
        max_length = len(text) // 2 if len(text) > min_length*2 else min_length*2
        input_text = "summarize: " + text
        inputs = self.tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = self.model.generate(
            inputs['input_ids'],
            max_length=max_length,
            min_length=min_length,
            length_penalty=1.0,
            num_beams=4,
            early_stopping=True
        )
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summary.replace('summary:', '')
        self.logger.info(f"Memory summarized from len {len(text)} to {len(summary)}.")
        self.logger.info(f"Summarized text:\n{summary}")
        return summary
    
    #@timer_decorator
    def compress(self) -> str:
        """
        Compress (summarize) the memory using the model.
        """
        if self.tokenizer is None or self.model is None:
            self.logger.warning("No tokenizer or model to perform memory compression.")
            return
        for i in range(len(self.memory)):
            if self.memory[i]['role'] == 'system':
                continue
            if len(self.memory[i]['content']) > 1024:
                self.memory[i]['content'] = self.summarize(self.memory[i]['content'])
    
    def trim_text_to_max_ctx(self, text: str) -> str:
        """
        Truncate a text to fit within the maximum context size of the model.
        """
        ideal_ctx = self.get_ideal_ctx(self.model_provider)
        return text[:ideal_ctx] if ideal_ctx is not None else text
    
    #@timer_decorator
    def compress_text_to_max_ctx(self, text) -> str:
        """
        Compress a text to fit within the maximum context size of the model.
        """
        if self.tokenizer is None or self.model is None:
            self.logger.warning("No tokenizer or model to perform memory compression.")
            return text
        ideal_ctx = self.get_ideal_ctx(self.model_provider)
        if ideal_ctx is None:
            self.logger.warning("No ideal context size found.")
            return text
        while len(text) > ideal_ctx:
            self.logger.info(f"Compressing text: {len(text)} > {ideal_ctx} model context.")
            text = self.summarize(text)
        return text