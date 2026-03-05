---
title: AI Employee Skills
version: 2.0
tier: silver
---

# Available Skills

## Skill 1: GmailWatcherTrigger
**Purpose:** Read Gmail watcher files from Needs_Action folder and extract email-related tasks.

**Usage:**
```yaml
skill: "gmail-watcher-trigger"
```

**Example Prompt:** "Check Needs_Action for any Gmail watcher files and summarize the email tasks."

**Input:** .md files in Needs_Action/ folder containing Gmail notifications

**Output:** Structured summary of sender, subject, urgency, and required action

---

## Skill 2: WhatsAppWatcherTrigger
**Purpose:** Read WhatsApp watcher files from Needs_Action folder and extract message-related tasks.

**Usage:**
```yaml
skill: "whatsapp-watcher-trigger"
```

**Example Prompt:** "Check Needs_Action for any WhatsApp watcher files and summarize the messages."

**Input:** .md files in Needs_Action/ folder containing WhatsApp notifications

**Output:** Structured summary of sender, message content, urgency, and required action

---

## Skill 3: CreatePlan
**Purpose:** Create a Plan.md file in /Plans folder with checkboxes for task breakdown.

**Usage:**
```yaml
skill: "create-plan"
```

**Example Prompt:** "Create a plan for processing the invoice payment with approval steps."

**Input:** Task description and required steps

**Output:** Plan.md file in /Plans/ with markdown checkboxes for each step

**Format:**
```markdown
# Plan: [Task Name]
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3
```

---

## Skill 4: CreateApproval
**Purpose:** Create an approval file in /Pending_Approval folder for sensitive actions (email, payment, etc.).

**Usage:**
```yaml
skill: "create-approval"
```

**Example Prompt:** "Create an approval request for sending an email to the client."

**Input:** Action type, description, recipient/details, risk level

**Output:** Approval request file in /Pending_Approval/ awaiting user confirmation

**Format:**
```markdown
# Approval Request
- **Action:** [email/payment/other]
- **Description:** [details]
- **Status:** Pending
- [ ] Approved
- [ ] Rejected
```

---

## Skill 5: UseMCP
**Purpose:** Call external MCP server (e.g., email MCP) to execute actions after approval is granted.

**Usage:**
```yaml
skill: "use-mcp"
```

**Example Prompt:** "Use the email MCP server to send the approved email to the recipient."

**Input:** MCP server name, action type, payload data, approval reference

**Output:** Confirmation of MCP action execution

**Supported MCP Servers:**
- email: Send emails via connected email service
- payment: Process payments via connected payment gateway

---

## Skill 6: MoveToDone
**Purpose:** Move a processed file from Needs_Action folder to Done folder after task completion.

**Usage:**
```yaml
skill: "move-to-done"
```

**Example Prompt:** "Move the file Needs_Action/gmail-notification-001.md to Done folder."

**Input:** File path in Needs_Action/

**Output:** File moved to Done/ with timestamp preserved

---

# Workflow Examples

## Email Processing Workflow (Silver Tier)
1. **GmailWatcherTrigger** - Read Gmail notification from Needs_Action/
2. **CreatePlan** - Create plan with steps in /Plans/
3. **CreateApproval** - Create approval request in /Pending_Approval/ (for sending email)
4. *Wait for user approval*
5. **UseMCP** - Send email via email MCP server
6. **MoveToDone** - Move processed file to Done/
7. **Log Action** - Record completion in Logs/action-log.md

## WhatsApp Processing Workflow (Silver Tier)
1. **WhatsAppWatcherTrigger** - Read WhatsApp notification from Needs_Action/
2. **CreatePlan** - Create plan with steps in /Plans/
3. **CreateApproval** - Create approval request if action is sensitive
4. *Wait for user approval (if required)*
5. **UseMCP** - Execute action via MCP server (if applicable)
6. **MoveToDone** - Move processed file to Done/
7. **Log Action** - Record completion in Logs/action-log.md

---

# How to Use Skills in Prompts

When you want me to use a specific skill, reference it in your prompt using one of these patterns:

1. **Direct skill invocation:** I will automatically invoke the relevant skill tool when you mention a task that matches a skill's purpose.

2. **Explicit request:** Say "use the [skill-name] skill to..." or "invoke skill: [skill-name]"

3. **Task-based:** Describe the task naturally, and I'll match it to the appropriate skill:
   - "Check Gmail notifications" → GmailWatcherTrigger skill
   - "Check WhatsApp messages" → WhatsAppWatcherTrigger skill
   - "Create a plan for this task" → CreatePlan skill
   - "Request approval for sending email" → CreateApproval skill
   - "Send the email using MCP" → UseMCP skill
   - "Mark this as complete" → MoveToDone skill
   - "Log what you just did" → Log Action skill

**Note:** Skills are executed via the `skill` tool. Only one skill can run at a time.

**Tier Requirements:**
- **Silver Tier:** Requires approval for sensitive actions (email, payment) before MCP execution
- All watcher triggers read from Needs_Action/ folder only
- Plans are stored in /Plans/ folder
- Approval requests are stored in /Pending_Approval/ folder
- Completed files are moved to /Done/ folder
