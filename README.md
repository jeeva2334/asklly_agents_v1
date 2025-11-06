# Asklly Agents

This project is a Python-based application that uses an agent-driven architecture to perform tasks, including web browsing and information retrieval. It is powered by a FastAPI backend and uses the Brave Search API for web searches.

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python 3.10 or higher
- Google Chrome browser

## Setup Instructions

Follow these steps to get the project up and running on your local machine.

### 1. Clone the Repository

First, clone the project repository to your local machine:
```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On macOS and Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install all the required Python packages using the `requirements.txt` file. It's recommended to use `uv` for faster installation.
```bash
pip install uv
uv pip install -r requirements.txt
```
If you don't have `uv`, you can use `pip`:
```bash
pip install -r requirements.txt
```

### 4. Install ChromeDriver

This project uses Selenium to control a web browser, which requires the appropriate WebDriver. For Google Chrome, you need to install ChromeDriver.

You can download the version that matches your installed Chrome browser from the [Chrome for Testing availability dashboard](https://googlechromelabs.github.io/chrome-for-testing/).

After downloading, make sure the `chromedriver` executable is in your system's `PATH` or in the root directory of this project.

### 5. Configure the Application

The application's settings are managed in the `config.ini` file. Before running the application, you need to add your Brave Search API key.

1.  Find the `config.ini` file in the root of the project.
2.  Open the file and locate the `[BROWSER]` section.
3.  Replace `your_brave_api_key_here` with your actual Brave Search API key.

```ini
[BROWSER]
headless_browser = True
stealth_mode = False
```

## Running the Project

Once you have completed the setup steps, you can start the application's web server.

From the root directory of the project, run the following command:
```bash
python api.py
```
This will start the FastAPI server using `uvicorn` on `http://0.0.0.0:8844`.

You can now send requests to the API. For example, you can interact with the `/agent` endpoint to ask questions and have the agent perform web searches.