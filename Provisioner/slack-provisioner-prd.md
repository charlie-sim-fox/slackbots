
---

## Admin Steps to Perform (Displayed in #care_tools)
1. Add new user in Okta preview.
2. In **Title** field add: **FOX TESTER**.
3. In Okta Admin, add user to **FOX ONE Care**.
4. Update status with Provisioner Slackbot.

---

## Personas
- **Requester:** Needs Salesforce access (MVP focuses on UAT).
- **Admin/Provisioner:** Performs Okta Preview setup and updates request status.

---

## Success Metrics
- Bot creates an “In Progress” request and posts to `#care_tools` within < 1 minute.
- Admin can update status with a single click.
- Reduced “how do I log in?” follow-ups (Quick Start Guide sent automatically on completion).

---

## Non-Goals (Explicit)
- Automated provisioning in Okta/Salesforce (human-admin steps remain).
- SLA enforcement/escalations (future enhancement).
- Handling requests outside allowlisted channels (initially).

---

# UX / Flows

## Flow A — Keyword-Triggered Request (Happy Path)
1. User posts in an allowlisted channel containing a keyword.
2. Bot responds (prefer **ephemeral**) asking:
   - “Do you want to request a UAT account or report an issue?”
3. User selects **Request UAT account**.
4. Bot opens a **modal** collecting:
   - First Name (required)
   - Last Name (required)
   - Email (required)
   - (Optional) Environment: UAT / Training / Production (default UAT for MVP)
5. On submit:
   - Bot generates a 7-char tracking ID.
   - Bot stores the request (status = **In Progress**).
   - Bot posts request details + admin steps + status action controls in `#care_tools`.
   - Bot posts back to the origin thread: “Request submitted — Status: In Progress — Tracking ID …”
6. Admin updates status in `#care_tools`.
7. Bot posts back to the original thread:
   - “Your request is **Complete**.” + Quick Start Guide  
   OR
   - “Your request is **Blocked**.” (+ optional reason / next steps)

---

## Flow B — Slash Command: `/provisioner-help`
- User types `/provisioner-help`
- Bot returns an **ephemeral** message containing:
  - Quick Start Guide
  - Button: “Start UAT account request” (opens request modal)

---

## Flow C — Report an Issue (Optional/MVP+)
- Same entry points (keyword or `/provisioner-help`)
- Modal collects:
  - Issue type (can’t find tile / SSO confusion / MFA setup / other)
  - Description
  - Email
- Bot posts issue request to `#care_tools` with tracking ID and allows status updates.

---

# Technical Spec

## Platform / Implementation
- Slack app built with **Slack Bolt** (Node.js or Python) + Slack Web API
- Deployed as:
  - Web service (ECS/Heroku/etc.) **or**
  - Serverless (AWS Lambda + API Gateway)
- **Persistent storage required** (DB) for request status + routing replies to origin channel/thread.

---

## Slack Capabilities Used
- **Events API**: receive messages from channels (`message.channels`)
- **Interactivity**: buttons/selects + modal submission callbacks
- **Modals**: `views.open` for collecting details
- **Posting messages**: `chat.postMessage` (including threaded replies)
- **Slash commands**: `/provisioner-help`

---

## Slack App Configuration

### Event Subscriptions
- Enable Events API and set Request URL
- Handle Slack URL verification challenge
- Subscribe to:
  - `message.channels` (public channel messages)
  - (Optional for private channels) `message.groups` / relevant private message events depending on workspace setup

### Interactivity
- Enable interactivity and set a single Request URL for:
  - `block_actions`
  - `view_submission`

### Slash Command
- Configure `/provisioner-help` pointing to the command endpoint

---

## OAuth Scopes (Minimum Recommended)
- `channels:history` — read channel messages (where app is present)
- `chat:write` — post messages and thread replies
- `commands` — enable slash commands

Optional:
- `users:read.email` — only if you want to auto-fill email from Slack profile (not required)

---

# System Architecture

## Endpoints
1. `POST /slack/events`
   - Events API payloads (including URL verification + `message.*`)
2. `POST /slack/interactivity`
   - Interactivity payloads (`block_actions`, `view_submission`)
3. `POST /slack/commands`
   - Slash command payload for `/provisioner-help`

---

## Data Model (DB)

### `ProvisionRequest`
- `tracking_id` (string, 7 chars, unique)
- `status` (`IN_PROGRESS` | `COMPLETE` | `BLOCKED`)
- `request_type` (`ACCESS_REQUEST` | `ISSUE`)
- `environment` (`UAT` | `TRAINING` | `PRODUCTION`)
- `requester_first_name`
- `requester_last_name`
- `requester_email`
- `requester_slack_user_id`
- `origin_channel_id`
- `origin_message_ts` (thread root)
- `care_tools_channel_id`
- `care_tools_message_ts` (for updating the admin message if needed)
- `admin_updated_by_user_id` (nullable)
- `blocked_reason` (nullable)
- `created_at`
- `updated_at`

---

## Tracking ID
- Random **uppercase alphanumeric**, length = 7
- Enforce uniqueness with DB constraint; on collision, regenerate

---

## Idempotency / Retries
Slack may retry events/interactions. Ensure handlers are idempotent:
- Store and dedupe by Slack `event_id` (Events API)
- Deduplicate modal submissions using a stable key (e.g., `view.id` + internal request id)
- Guard against double-clicks on admin actions (check status already set)

---

# Block Kit / UI Design (High Level)

## 1) Keyword-detected Prompt (Ephemeral)
- Text: “I can help with Salesforce UAT access.”
- Buttons:
  - “Request UAT account”
  - “Report an issue”
  - “Quick Start Guide”

## 2) Request Modal
**Title:** “Request Salesforce Access”  
**Inputs:**
- First Name (required)
- Last Name (required)
- Email (required)
- Environment (static_select; default UAT in MVP)
**Submit:** “Submit request”

## 3) Admin Message in `#care_tools`
- Header: `Provisioning Request — <TRACKING_ID>`
- Fields:
  - Requester: name + email + Slack @mention
  - Environment: UAT
  - Origin: channel + thread context
  - Status: In Progress
- Section: “Admin Steps to Perform” (checklist)
- Admin control:
  - MVP option: two buttons “Mark Complete” / “Mark Blocked”
  - Enhanced option: select menu Complete/Blocked + “Post status update”

## 4) Origin Thread Update
- Always include:
  - “Your request is **<STATUS>**. Tracking ID: <ID>”
- If Complete:
  - Append Quick Start Guide
- If Blocked:
  - Append blocked reason (if collected) + next steps

---

# Validation Rules
- First/Last name: non-empty
- Email: basic validation (must contain `@` and `.`, optional stricter regex)
- Environment: must be one of allowed values

---

# Security & Compliance
- Verify Slack signatures for:
  - Events
  - Interactivity
  - Slash commands
- Apply channel allowlist filtering (only respond in approved channels)
- Avoid posting requester email publicly; keep PII in `#care_tools` only

---

# Acceptance Criteria (MVP)
- [ ] Keyword in allowlisted channel triggers ephemeral prompt.
- [ ] Modal collects First/Last/Email and generates 7-char tracking ID.
- [ ] Request is stored and posted to `#care_tools` with admin steps + status controls.
- [ ] Admin click updates status and posts a threaded message in original channel.
- [ ] `/provisioner-help` returns Quick Start Guide + “Start request” button.
- [ ] Idempotent handling of Slack retries and repeated clicks.

---

# Recommended MVP Cut (Fastest Ship)
- UAT-only environment in v1 (since Quick Start Guide is UAT-specific).
- Two admin buttons in `#care_tools`: **Mark Complete** / **Mark Blocked**.
- Skip blocked reason in v1; add modal for reason in v1.1.