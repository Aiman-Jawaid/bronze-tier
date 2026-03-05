# Personal AI Employee – Bronze Tier

This is the **Bronze Tier** implementation of the "Personal AI Employee" hackathon project (Panaversity / Hackathon 0 – Building Autonomous FTEs in 2026).

The goal is to create a local-first, privacy-focused AI assistant that monitors inputs and processes tasks using Claude Code + VS Code workspace.

## Features (Bronze Tier – Minimum Viable)

- Obsidian-like folder structure replaced with simple VS Code workspace
- Folders: Inbox, Needs_Action, Done, Logs
- Dashboard.md – basic status overview
- Company_Handbook.md – rules & guidelines
- SKILL.md – Agent Skills definitions
- File system watcher (`file_watcher.py`): monitors /Inbox for dropped files → copies to /Needs_Action with metadata
- Basic orchestrator (`orchestrator.py`): processes Needs_Action files, updates Dashboard, moves to Done
- Claude Code integration for file read/write and task processing
- Ralph Wiggum-style loop support (task completion detection)

## Tech Stack

- **Reasoning Engine**: Claude Code (Anthropic)
- **IDE/Dashboard**: VS Code (workspace folder)
- **Watchers**: Python + watchdog library
- **Orchestration**: Python scripts
- **File format**: Markdown (.md)

## Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/personal-ai-employee-bronze.git
   cd personal-ai-employee-bronze

Install dependencies:Bashpip install watchdog
Open the folder in VS Code:
File → Open Folder → select this project folder

Install Claude Code extension in VS Code (search "Claude Code" by Anthropic)
Run the file watcher (background):Bashpython file_watcher.py(Recommended: use PM2 or nohup for persistent running)
Run orchestrator:Bashpython orchestrator.py
Test:
Drop any file (txt, pdf, image) into /Inbox
Wait → file should appear in /Needs_Action with metadata .md
Orchestrator processes it → Dashboard.md updates → file moves to /Done


Folder Structure
textAI_Employee_Folder/
├── Inbox/                  # Drop client files here
├── Needs_Action/           # Watcher creates .md files here
├── Done/                   # Processed files go here
├── Logs/                   # Log files
├── Dashboard.md            # Real-time summary
├── Company_Handbook.md     # Rules
├── SKILL.md                # Agent Skills
├── file_watcher.py
├── orchestrator.py
└── .env                    # (optional for future)
Limitations (Bronze Tier)

Only file-drop watcher (no Gmail/WhatsApp yet)
No MCP servers / external actions
No human-in-the-loop approval flow
Basic processing (no complex planning)
