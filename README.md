# LangGraph-Agent-Workflow

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

## Description
The LangGraph-Agent-Workflow is an autonomous Python-based AI agent designed for Supply Chain and Inventory management. It utilizes LangGraph to orchestrate complex workflows, seamlessly bridging unstructured industrial document analysis (like PDFs) with structured SQL database operations. 

Instead of manual data entry, the system uses a ReAct (Reasoning and Acting) loop with persistent memory. The agent autonomously reads uploaded documents, extracts relevant product and pricing information, and decides which database tools to execute to keep the inventory up to date.

**Features:**
* **PDF Extraction & Highlighting:** Autonomously finds and highlights key data in uploaded PDFs.
* **SQL Orchestration:** Connects directly to an SQLite backend to check, update, add, or delete inventory items.
* **Persistent Memory:** Retains conversational context across the session using LangGraph's `MemorySaver`.

## Visuals
[![Demo Video](https://img.shields.io/badge/🎥_Watch_Demo_Video-blue?style=for-the-badge)](INSERT_YOUR_VIDEO_LINK_HERE)


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required dependencies. It is highly recommended to use a virtual environment.

```bash
# 1. Clone the repository
git clone [https://github.com/aria-blip/LangGraph-Agent-Workflow.git](https://github.com/aria-blip/LangGraph-Agent-Workflow.git)
cd LangGraph-Agent-Workflow

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment Variables
cp .env.example .env
# Open the .env file and add your GROQ_API_KEY
