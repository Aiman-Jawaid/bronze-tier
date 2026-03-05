#!/usr/bin/env python3
"""
Orchestrator for AI Employee - Silver Tier
Polls Needs_Action folder, processes Gmail + WhatsApp files, handles approvals, and executes via MCP.
"""

import os
import sys
import logging
import time
import shutil
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

import schedule

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
NEEDS_ACTION_DIR = BASE_DIR / "Needs_Action"
DONE_DIR = BASE_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"
PLANS_DIR = BASE_DIR / "Plans"
PENDING_APPROVAL_DIR = BASE_DIR / "Pending_Approval"
APPROVED_DIR = BASE_DIR / "Approved"
DASHBOARD_FILE = BASE_DIR / "Dashboard.md"
LOG_FILE = LOGS_DIR / "orchestrator.log"

# Silver Tier Settings
POLL_INTERVAL = 30  # seconds
MAX_LOOP_ITERATIONS = 5  # Ralph Wiggum style max iterations
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

# Ensure directories exist
for directory in [NEEDS_ACTION_DIR, DONE_DIR, LOGS_DIR, PLANS_DIR, PENDING_APPROVAL_DIR, APPROVED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SilverTierOrchestrator:
    """Orchestrator for Silver tier with Gmail + WhatsApp support."""
    
    def __init__(self):
        self.processed_files = set()
        self.loop_count = 0
        self.last_summary_time = None
    
    def read_file_content(self, file_path: Path) -> str:
        """Read content of a markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return ""
    
    def parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter from markdown content."""
        try:
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    yaml_content = parts[1].strip()
                    return yaml.safe_load(yaml_content) or {}
        except Exception as e:
            logger.warning(f"Error parsing frontmatter: {e}")
        return {}
    
    def get_file_type(self, metadata: Dict, content: str) -> str:
        """Determine file type: gmail, whatsapp, or unknown."""
        file_type = metadata.get("type", "").lower()
        
        if "gmail" in file_type or "gmail" in content.lower():
            return "gmail"
        elif "whatsapp" in file_type or "whatsapp" in content.lower():
            return "whatsapp"
        
        return "unknown"
    
    def extract_email_details(self, content: str) -> Dict:
        """Extract email details from Gmail notification."""
        details = {
            "from": "",
            "to": "",
            "subject": "",
            "priority": "normal",
            "needs_response": False
        }
        
        try:
            for line in content.split("\n"):
                line_lower = line.lower()
                if "**from:**" in line_lower:
                    details["from"] = line.split(":", 1)[1].strip().strip("*")
                elif "**to:**" in line_lower:
                    details["to"] = line.split(":", 1)[1].strip().strip("*")
                elif "**subject:**" in line_lower:
                    details["subject"] = line.split(":", 1)[1].strip().strip("*")
                elif "**priority:**" in line_lower:
                    details["priority"] = line.split(":", 1)[1].strip().strip("*").lower()
            
            # Check if response is needed
            if "action required" in content.lower() or "response" in content.lower():
                details["needs_response"] = True
        except Exception as e:
            logger.warning(f"Error extracting email details: {e}")
        
        return details
    
    def extract_whatsapp_details(self, content: str) -> Dict:
        """Extract WhatsApp message details."""
        details = {
            "from": "",
            "message": "",
            "priority": "normal",
            "needs_response": False
        }
        
        try:
            for line in content.split("\n"):
                line_lower = line.lower()
                if "**from:**" in line_lower:
                    details["from"] = line.split(":", 1)[1].strip().strip("*")
                elif "**priority:**" in line_lower:
                    details["priority"] = line.split(":", 1)[1].strip().strip("*").lower()
            
            # Extract recent messages
            if "## recent messages" in content.lower():
                messages_section = content.split("## Recent Messages", 1)[1]
                if "##" in messages_section:
                    messages_section = messages_section.split("##")[0]
                details["message"] = messages_section.strip()[:500]
            
            # Check if response is needed
            if "urgent" in content.lower() or "help" in content.lower() or "asap" in content.lower():
                details["needs_response"] = True
        except Exception as e:
            logger.warning(f"Error extracting WhatsApp details: {e}")
        
        return details
    
    def create_plan(self, file_name: str, file_type: str, details: Dict) -> Optional[Path]:
        """Create Plan.md in /Plans folder with checkboxes."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_name = f"plan_{timestamp}_{file_name.replace('.md', '')}.md"
            plan_path = PLANS_DIR / plan_name
            
            # Determine steps based on file type and details
            steps = [
                ("Review notification content", False),
                ("Determine required action", False),
            ]
            
            if details.get("needs_response") or file_type == "gmail":
                steps.append(("Draft response message", False))
                steps.append(("Create approval request for sending", False))
                steps.append(("Wait for approval", False))
                steps.append(("Send via MCP after approval", False))
            
            steps.append(("Update dashboard with completion", False))
            steps.append(("Move to Done folder", False))
            
            # Build plan content
            plan_content = f"""---
title: Plan for {file_name}
type: {file_type}
created: {datetime.now().isoformat()}
status: in_progress
---

# Plan: Process {file_type.upper()} Notification

**Source File:** {file_name}
**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Priority:** {details.get("priority", "normal").upper()}

## Steps

"""
            for i, (step, completed) in enumerate(steps, 1):
                checkbox = "[x]" if completed else "[ ]"
                plan_content += f"{checkbox} Step {i}: {step}\n"
            
            plan_content += f"""

## Details
- **From:** {details.get("from", "Unknown")}
- **Subject/Message:** {details.get("subject", details.get("message", "N/A")[:100])}
- **Priority:** {details.get("priority", "normal").upper()}

## Notes
- Auto-generated by Silver Tier Orchestrator
- Requires approval for email sending actions
"""
            
            with open(plan_path, "w", encoding="utf-8") as f:
                f.write(plan_content)
            
            logger.info(f"Created plan: {plan_path.name}")
            return plan_path
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return None
    
    def create_approval_request(self, file_name: str, file_type: str, details: Dict) -> Optional[Path]:
        """Create approval file in /Pending_Approval for sensitive actions."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            approval_name = f"approval_{timestamp}_{file_type}_{file_name.replace('.md', '')}.md"
            approval_path = PENDING_APPROVAL_DIR / approval_name
            
            action_type = "send_email" if file_type == "gmail" else "send_message"
            
            approval_content = f"""---
type: approval_request
action_type: {action_type}
created: {datetime.now().isoformat()}
status: pending
source_file: {file_name}
---

# Approval Request

## Action Details
- **Action Type:** {action_type.replace("_", " ").title()}
- **Source:** {file_type.upper()} notification
- **From:** {details.get("from", "Unknown")}
- **Subject/Recipient:** {details.get("to", details.get("subject", "N/A"))}
- **Priority:** {details.get("priority", "normal").upper()}

## Reason
Approval required for sending {file_type} response as per Silver Tier policy.

## Message Preview
{details.get("message", details.get("subject", "No preview available"))[:500]}

---
## Approval Decision
- [ ] **APPROVED** - Proceed with sending
- [ ] **REJECTED** - Do not send

## Metadata
- **Requested:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Approved By:** _Pending_
- **Approved At:** _Pending_
"""
            
            with open(approval_path, "w", encoding="utf-8") as f:
                f.write(approval_content)
            
            logger.info(f"Created approval request: {approval_path.name}")
            return approval_path
            
        except Exception as e:
            logger.error(f"Error creating approval request: {e}")
            return None
    
    def check_approval_status(self, source_file: str) -> Tuple[bool, bool]:
        """
        Check if approval exists and is approved.
        Returns: (approval_exists, is_approved)
        """
        try:
            # Check Pending_Approval first
            for approval_file in PENDING_APPROVAL_DIR.glob("*.md"):
                content = self.read_file_content(approval_file)
                if source_file in content:
                    if "[x] **approved**" in content.lower() or "[x] approved" in content.lower():
                        # Move to Approved folder
                        shutil.move(str(approval_file), str(APPROVED_DIR / approval_file.name))
                        logger.info(f"Approval granted: {approval_file.name}")
                        return (True, True)
                    elif "[x] **rejected**" in content.lower() or "[x] rejected" in content.lower():
                        logger.warning(f"Approval rejected: {approval_file.name}")
                        return (True, False)
                    return (True, False)  # Still pending
            
            # Check Approved folder
            for approval_file in APPROVED_DIR.glob("*.md"):
                content = self.read_file_content(approval_file)
                if source_file in content:
                    return (True, True)
            
            return (False, False)
            
        except Exception as e:
            logger.error(f"Error checking approval: {e}")
            return (False, False)
    
    def call_email_mcp(self, details: Dict) -> bool:
        """Call email MCP server to send email after approval."""
        try:
            logger.info(f"Calling Email MCP server at {MCP_SERVER_URL}")
            
            # For now, log the action (MCP integration would go here)
            # In production, this would make HTTP request to MCP server
            mcp_payload = {
                "action": "send_email",
                "to": details.get("to", ""),
                "subject": f"Re: {details.get("subject", "")}",
                "priority": details.get("priority", "normal"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Simulate MCP call (replace with actual HTTP request)
            logger.info(f"MCP Payload: {json.dumps(mcp_payload, indent=2)}")
            logger.info("Email MCP call simulated (configure MCP_SERVER_URL for real calls)")
            
            # TODO: Actual MCP integration
            # import requests
            # response = requests.post(f"{MCP_SERVER_URL}/email/send", json=mcp_payload)
            # return response.status_code == 200
            
            return True  # Simulated success
            
        except Exception as e:
            logger.error(f"Error calling email MCP: {e}")
            return False
    
    def update_dashboard(self, file_name: str, file_type: str, summary: str = "") -> bool:
        """Append processed file info to Dashboard.md under Recent Activity."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            activity_line = f"- [{timestamp}] {file_type.upper()}: {file_name}"
            if summary:
                activity_line += f" - {summary}"
            
            # Read current dashboard
            if DASHBOARD_FILE.exists():
                with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                logger.warning("Dashboard.md not found, creating new one")
                content = f"""---
title: AI Employee Dashboard
last_updated: {datetime.now().strftime("%Y-%m-%d")}
tier: silver
---

# Dashboard

## Recent Activity

## Statistics
- Total Processed: 0
- Gmail: 0
- WhatsApp: 0

"""
            
            # Find Recent Activity section and append
            if "## Recent Activity" in content:
                lines = content.split("\n")
                new_lines = []
                inserted = False
                for line in lines:
                    new_lines.append(line)
                    if line.strip() == "## Recent Activity" and not inserted:
                        new_lines.append(activity_line)
                        inserted = True
                content = "\n".join(new_lines)
            else:
                content += f"\n## Recent Activity\n{activity_line}\n"
            
            # Update last_updated
            content = content.replace(
                f"last_updated: {datetime.now().strftime('%Y-%m-%d')}",
                f"last_updated: {datetime.now().strftime('%Y-%m-%d')}"
            )
            
            # Write back
            with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"Dashboard updated: {activity_line}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            return False
    
    def move_to_done(self, file_path: Path) -> bool:
        """Move file from Needs_Action to Done folder."""
        try:
            dest_path = DONE_DIR / file_path.name
            shutil.move(str(file_path), str(dest_path))
            logger.info(f"Moved to Done: {file_path.name}")
            return True
        except Exception as e:
            logger.error(f"Error moving {file_path.name} to Done: {e}")
            return False
    
    def process_file(self, file_path: Path) -> bool:
        """
        Process a single file from Needs_Action (Silver Tier).
        Flow: Plan → Approval (if needed) → MCP → Dashboard → Done
        """
        logger.info(f"Processing: {file_path.name}")
        
        # Read content
        content = self.read_file_content(file_path)
        if not content:
            logger.warning(f"Empty or unreadable file: {file_path.name}")
            return False
        
        # Parse metadata
        metadata = self.parse_frontmatter(content)
        file_type = self.get_file_type(metadata, content)
        
        logger.info(f"File type: {file_type}")
        
        # Extract details based on type
        if file_type == "gmail":
            details = self.extract_email_details(content)
        elif file_type == "whatsapp":
            details = self.extract_whatsapp_details(content)
        else:
            details = {"priority": "normal", "needs_response": False}
        
        # Step 1: Create Plan
        plan_path = self.create_plan(file_path.name, file_type, details)
        if not plan_path:
            logger.warning("Failed to create plan, continuing anyway")
        
        # Step 2: Create Approval if response needed
        approval_needed = details.get("needs_response", False) or file_type == "gmail"
        approval_granted = False
        
        if approval_needed:
            logger.info("Approval required for this action")
            approval_path = self.create_approval_request(file_path.name, file_type, details)
            
            if approval_path:
                # Wait for approval (poll)
                logger.info("Waiting for approval...")
                max_approval_wait = 300  # 5 minutes max
                wait_start = time.time()
                
                while time.time() - wait_start < max_approval_wait:
                    exists, approved = self.check_approval_status(file_path.name)
                    if exists and approved:
                        approval_granted = True
                        logger.info("Approval granted!")
                        break
                    elif exists and not approved:
                        logger.warning("Approval rejected, skipping MCP action")
                        break
                    time.sleep(5)  # Check every 5 seconds
                else:
                    logger.warning("Approval timeout, skipping MCP action")
            else:
                logger.warning("Failed to create approval request")
        else:
            approval_granted = True  # No approval needed
        
        # Step 3: Call MCP if approval granted
        mcp_success = False
        if approval_granted and approval_needed:
            logger.info("Executing MCP action...")
            if file_type == "gmail":
                mcp_success = self.call_email_mcp(details)
            elif file_type == "whatsapp":
                # WhatsApp MCP would go here
                logger.info("WhatsApp action completed (no MCP needed for read-only)")
                mcp_success = True
        elif not approval_needed:
            mcp_success = True  # No MCP action needed
        
        # Step 4: Update Dashboard
        summary = f"{file_type.upper()} processed"
        if mcp_success:
            summary += " - MCP action completed"
        elif approval_needed and not approval_granted:
            summary += " - Approval pending/rejected"
        
        self.update_dashboard(file_path.name, file_type, summary)
        
        # Step 5: Move to Done
        if not self.move_to_done(file_path):
            logger.error(f"Failed to move {file_path.name} to Done")
            return False
        
        logger.info(f"Successfully processed: {file_path.name}")
        return True
    
    def get_pending_files(self) -> List[Path]:
        """Get list of unprocessed .md files in Needs_Action."""
        pending = []
        if NEEDS_ACTION_DIR.exists():
            for file_path in NEEDS_ACTION_DIR.glob("*.md"):
                if file_path.name not in self.processed_files:
                    pending.append(file_path)
        return sorted(pending, key=lambda p: p.stat().st_mtime)
    
    def run_daily_summary(self):
        """Generate daily summary at 8 AM."""
        try:
            now = datetime.now()
            summary = f"""
## Daily Summary - {now.strftime("%Y-%m-%d %H:%M")}

- Orchestrator running for Silver Tier
- Gmail + WhatsApp watchers active
- Pending files: {len(self.get_pending_files())}
- Processed this session: {len(self.processed_files)}
"""
            logger.info(summary)
            self.last_summary_time = now
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
    
    def run(self):
        """Main orchestrator loop with Ralph Wiggum style max iterations."""
        logger.info("=" * 50)
        logger.info("AI Employee Orchestrator (Silver Tier)")
        logger.info(f"Monitoring: {NEEDS_ACTION_DIR}")
        logger.info(f"Poll interval: {POLL_INTERVAL} seconds")
        logger.info(f"Max loop iterations: {MAX_LOOP_ITERATIONS}")
        logger.info("=" * 50)
        logger.info("Press Ctrl+C to stop...")
        
        # Schedule daily 8 AM summary
        schedule.every().day.at("08:00").do(self.run_daily_summary)
        
        try:
            while True:
                # Run scheduled tasks
                schedule.run_pending()
                
                # Ralph Wiggum style loop counter
                self.loop_count += 1
                if self.loop_count > MAX_LOOP_ITERATIONS:
                    logger.warning(f"Max iterations ({MAX_LOOP_ITERATIONS}) reached, resetting")
                    self.loop_count = 0
                    time.sleep(60)  # Cool down
                    continue
                
                # Get pending files
                pending = self.get_pending_files()
                
                if pending:
                    logger.info(f"Found {len(pending)} pending file(s)")
                    for file_path in pending:
                        if self.process_file(file_path):
                            self.processed_files.add(file_path.name)
                            self.loop_count = 0  # Reset on successful processing
                else:
                    logger.debug("No pending files, sleeping...")
                    self.loop_count = 0  # Reset when idle
                
                # Sleep for poll interval
                time.sleep(POLL_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("Shutdown signal received...")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)
        
        logger.info("Orchestrator stopped.")


def main():
    """Entry point."""
    orchestrator = SilverTierOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
