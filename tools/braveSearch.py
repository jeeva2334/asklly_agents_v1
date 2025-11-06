import requests
import os

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.tools import Tools
from bs4 import BeautifulSoup

class braveSearch(Tools):
    def __init__(self, api_key: str = None):
        """
        A tool for searching the Brave Search API and extracting URLs and titles.
        """
        super().__init__()
        self.tag = "web_search"
        self.name = "braveSearch"
        self.description = "A tool for searching the Brave Search API for web search"
        self.api_key = os.getenv("BRAVE_API_KEY") or api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        if not self.api_key:
            raise ValueError("Brave Search API key must be provided either as an argument or via the BRAVE_API_KEY environment variable.")


    def get_page_content(self, url: str) -> str:
        """
        Get the text content of a single page using requests and BeautifulSoup.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text
        except requests.exceptions.RequestException as e:
            return f"Error getting page content for {url}: {e}"

    def execute(self, blocks: list, safety: bool = False) -> str:
        """Executes a search query against the Brave Search API and extracts URLs and titles."""
        if not blocks:
            return "Error: No search query provided."

        query = blocks[0].strip()
        if not query:
            return "Error: Empty search query provided."

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query
        }
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            search_results = response.json()
            results = []
            if "web" in search_results and "results" in search_results["web"]:
                for result in search_results["web"]["results"][:3]: # Get top 3 results
                    page_content = self.get_page_content(result.get('url'))
                    results.append(f"Title:{result.get('title', 'No Title')}\nSnippet:{result.get('description', 'No Description')}\nLink:{result.get('url', 'No URL')}\nContent:{page_content}")
            if len(results) == 0:
                return "No search results, web search failed."
            return "\n\n".join(results)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Brave Search API request failed: {e}") from e

    def execution_failure_check(self, output: str) -> bool:
        """
        Checks if the execution failed based on the output.
        """
        return "Error" in output

    def interpreter_feedback(self, output: str) -> str:
        """
        Feedback of web search to agent.
        """
        if self.execution_failure_check(output):
            return f"Web search failed: {output}"
        return f"Web search result:\n{output}"