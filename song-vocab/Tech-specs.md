# Tech Specs

## Business Goal
We aim to develop a program that searches the internet for **song lyrics** in a specified **language** and extracts **vocabulary words** from the lyrics. The extracted vocabulary will be stored in a **database** for further analysis and use.

## Technical Requirements

- **FastAPI** (for API framework)
- **Ollama** via the Ollama Python SDK  
  - Uses **Mistral 7B** as the primary language model
- **Instructor** (for structured JSON output)
- **SQLite3** (for database storage)
- **duckduckgo-search** (to search for lyrics online)

---

## API Endpoints

### **GetLyrics** → `POST /api/agent`

#### **Behavior**
This endpoint interacts with an **agent** that follows the **ReAct framework**, allowing it to:
1. **Search the internet** for multiple versions of the target song lyrics.
2. **Analyze and select** the most accurate lyrics.
3. **Extract vocabulary** from the lyrics and format it into a structured response.

#### **Available Tools**
The agent has access to the following tools:
- `tools/extract_vocabulary.py` (Parses lyrics and extracts vocabulary)
- `tools/get_page_content.py` (Fetches webpage content)
- `tools/search_web.py` (Searches the internet for lyrics)

---

## Request & Response Structure

### **JSON Request Parameters**
| Parameter         | Type   | Description |
|------------------|--------|-------------|
| `message_request` | `str` | A string describing the **song** and/or **artist** to search for on the internet. |

### **JSON Response**
| Field       | Type   | Description |
|------------|--------|-------------|
| `lyrics`    | `str`  | The full lyrics of the song. |
| `vocabulary` | `list` | A list of **vocabulary words** extracted from the lyrics. |
