---
type: approval_request
action_type: send_email
created: 2026-02-27T10:30:20
status: approved
source_file: whatsapp_20260227_103000_urgent_client.md
---

# Approval Request

## Action Details
- **Action Type:** Send Email
- **Source:** WHATSAPP notification
- **From:** John Smith (Client)
- **To:** john.smith@client.com
- **Subject:** Re: Urgent - Invoice Request
- **Priority:** HIGH

## Reason
Approval required for sending email response as per Silver Tier policy.

## Email Draft

**To:** john.smith@client.com
**Subject:** Re: Urgent - Invoice Request

**Body:**
```
Hi John,

Thank you for your message.

Yes, the invoice is ready. I'm sending it to you right away. 
The payment can be processed today as requested.

Invoice #INV-2026-0227 is attached.

Please confirm receipt.

Best regards,
AI Employee
```

---
## Approval Decision

- [x] **APPROVED** - Proceed with sending email
- [ ] **REJECTED** - Do not send email

## Metadata
- **Requested:** 2026-02-27 10:30:20
- **Approved By:** User (Silver Tier Test)
- **Approved At:** 2026-02-27 10:32:00

---
## After Approval
Once moved to `/Approved` folder, the orchestrator will:
1. Detect the approval status
2. Call Email MCP server at http://localhost:8000/send_email
3. Send the email via Gmail SMTP
4. Update Dashboard.md
5. Move all related files to /Done
