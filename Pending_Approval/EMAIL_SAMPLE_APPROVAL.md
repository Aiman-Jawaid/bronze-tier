---
type: approval_request
action_type: send_email
created: 2026-02-27T10:00:00
status: pending
source_file: gmail_notification_example.md
---

# Approval Request

## Action Details
- **Action Type:** Send Email
- **Source:** GMAIL notification
- **From:** client@example.com
- **To:** partner@company.com
- **Subject:** Re: Q1 Budget Review Meeting
- **Priority:** HIGH

## Reason
Approval required for sending email response as per Silver Tier policy.

## Email Draft

**To:** partner@company.com
**Subject:** Re: Q1 Budget Review Meeting

**Body:**
```
Hi Partner,

Thank you for your email regarding the Q1 budget review.

I've reviewed the documents and confirm the following:
- Budget allocation: $50,000
- Timeline: March 1-31, 2026
- Deliverables: As outlined in attachment

Please let me know if you need any clarification.

Best regards,
AI Employee
```

---
## Approval Decision

**Instructions:**
1. Review the email content above
2. To APPROVE: Change `[ ]` to `[x]` under APPROVED and move this file to `/Approved` folder
3. To REJECT: Change `[ ]` to `[x]` under REJECTED and move to `/Done` folder

- [ ] **APPROVED** - Proceed with sending email
- [ ] **REJECTED** - Do not send email

## Metadata
- **Requested:** 2026-02-27 10:00:00
- **Approved By:** _Pending_
- **Approved At:** _Pending_

---
## After Approval
Once moved to `/Approved` folder, the orchestrator will:
1. Detect the approval status
2. Call Email MCP server at http://localhost:8000/send_email
3. Send the email via Gmail SMTP
4. Update Dashboard.md
5. Move all related files to /Done
