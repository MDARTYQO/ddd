# Gemini CLI Agent

This project is a command-line interface (CLI) chat agent powered by Google's Gemini model.

It allows you to interact with the Gemini model to execute shell commands on your local machine, enabling you to create, delete, and read files, run programs, and perform any other action available through the command line, all using natural language.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your API key:**
    - Create a `.env` file in the root directory.
    - Add your Gemini API key to the `.env` file:
      ```
      GEMINI_API_KEY="YOUR_API_KEY_HERE"
      ```

## Usage

Run the main script:
```bash
python main.py
```
