# Trello Import & GitHub Sync Guide

## 📥 Part 1: Import CSV to Trello

### Method 1: Direct CSV Import (Recommended)

1. **Create Your Trello Board**
   - Go to [trello.com](https://trello.com)
   - Click "Create new board"
   - Name: `VirtPLC SCRUM Board`
   - Set workspace and visibility

2. **Create Lists First** (Trello requires lists before import)
   ```
   Create these 7 lists in this exact order:
   1. 📋 Backlog
   2. 🎯 Sprint 3 - TODO
   3. 🔄 Sprint 3 - IN PROGRESS
   4. 🔴 BLOCKED
   5. ✅ Sprint 3 - DONE
   6. 📦 Sprint 2 - DONE
   7. 🏆 Sprint 1 - DONE
   ```

3. **Import the CSV**
   - Open your board
   - Click on board menu (three dots, top right)
   - Select **"More"** → **"Print and export"**
   - Click **"Import"**
   - Choose **"Trello"** as source
   - Upload `.github/trello-import.csv`
   - Map the columns:
     - Name → Card Name
     - Description → Card Description
     - List → List Name
     - Labels → Labels
     - Due Date → Due Date
     - Members → Members (you'll need to add team members first)
     - Story Points → Custom Field (create if doesn't exist)
     - Checklist Items → Checklist
   - Click **"Import"**

4. **Verify Import**
   - Check that all 27 cards are imported
   - Verify cards are in correct lists
   - Confirm labels are applied

### Method 2: Trello API Import (Programmatic)

If you prefer automation, use this script:

```bash
# Install dependencies
npm install node-trello

# Run import script (see trello-import.js below)
node .github/scripts/trello-import.js
```

---

## 🔄 Part 2: GitHub ↔ Trello Sync Automation

### Option A: GitHub Power-Up (Easiest - No Code)

1. **Enable GitHub Power-Up on Trello**
   - Open your Trello board
   - Click "Power-Ups" in menu
   - Search for "GitHub"
   - Click "Add" on official GitHub Power-Up
   - Authorize GitHub access

2. **Link Repository**
   - Click "GitHub" in Power-Up menu
   - Connect to repository: `Dedzsinator/VirtPLC`
   - Authorize access

3. **Auto-Link Commits to Cards**
   
   **In your git commits, use these formats:**
   ```bash
   # Link to specific card
   git commit -m "Fix login CORS issue https://trello.com/c/CARD_ID"
   
   # Or use card short link
   git commit -m "Implement MCP tool calling #MCP-SERVER"
   ```

   **Trello will automatically:**
   - Attach commits to cards
   - Show commit messages on cards
   - Link PRs when mentioned
   - Show branch information

### Option B: GitHub Actions Automation (Advanced - Full Control)

Create automated workflows that sync based on events:

#### 1. Create GitHub Action Workflow

File: `.github/workflows/trello-sync.yml`

```yaml
name: Trello Sync

on:
  issues:
    types: [opened, closed, labeled]
  pull_request:
    types: [opened, closed, merged]
  push:
    branches: [main, release]

jobs:
  sync-to-trello:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Sync to Trello
        uses: actions/github-script@v7
        env:
          TRELLO_API_KEY: ${{ secrets.TRELLO_API_KEY }}
          TRELLO_TOKEN: ${{ secrets.TRELLO_TOKEN }}
          TRELLO_BOARD_ID: ${{ secrets.TRELLO_BOARD_ID }}
        with:
          script: |
            const fetch = require('node-fetch');
            
            // Get commit message
            const commit = context.payload.head_commit;
            const message = commit?.message || '';
            
            // Extract card reference (e.g., "CARD-123" or card URL)
            const cardMatch = message.match(/(?:https:\/\/trello\.com\/c\/|#)([a-zA-Z0-9]+)/);
            
            if (cardMatch) {
              const cardId = cardMatch[1];
              
              // Add commit as comment to Trello card
              const comment = `✅ Commit pushed: ${commit.message}\n` +
                            `👤 Author: ${commit.author.name}\n` +
                            `🔗 [View commit](${commit.url})`;
              
              await fetch(
                `https://api.trello.com/1/cards/${cardId}/actions/comments?` +
                `key=${process.env.TRELLO_API_KEY}&token=${process.env.TRELLO_TOKEN}`,
                {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ text: comment })
                }
              );
            }
```

#### 2. Setup Trello API Credentials

**Get Trello API Key & Token:**

1. Go to https://trello.com/power-ups/admin
2. Click "New" → "Create Power-Up"
3. Get your API Key
4. Generate a Token: https://trello.com/1/authorize?key=YOUR_KEY&name=VirtPLC&expiration=never&response_type=token&scope=read,write

**Add to GitHub Secrets:**

1. Go to your GitHub repo
2. Settings → Secrets and variables → Actions
3. Add secrets:
   ```
   TRELLO_API_KEY: your-api-key
   TRELLO_TOKEN: your-token
   TRELLO_BOARD_ID: your-board-id (from board URL)
   ```

#### 3. Advanced Automation Rules

**Auto-move cards based on PR status:**

```yaml
# When PR is merged → Move card to DONE
- name: Move card to DONE on PR merge
  if: github.event.pull_request.merged == true
  run: |
    # Extract card ID from PR description
    CARD_ID=$(echo "${{ github.event.pull_request.body }}" | grep -oP 'trello.com/c/\K[a-zA-Z0-9]+')
    
    # Get DONE list ID
    DONE_LIST_ID="your-done-list-id"
    
    # Move card
    curl -X PUT "https://api.trello.com/1/cards/${CARD_ID}?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}&idList=${DONE_LIST_ID}"
```

**Auto-create cards from GitHub Issues:**

```yaml
- name: Create Trello card from GitHub Issue
  if: github.event.action == 'opened'
  run: |
    curl -X POST "https://api.trello.com/1/cards?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}" \
      -d "idList=${TRELLO_TODO_LIST_ID}" \
      -d "name=[${{ github.event.issue.number }}] ${{ github.event.issue.title }}" \
      -d "desc=${{ github.event.issue.body }}" \
      -d "due=null"
```

### Option C: Webhook Integration (Real-time Sync)

**1. Setup Trello Webhook**

```bash
# Create webhook to notify GitHub on card changes
curl -X POST "https://api.trello.com/1/webhooks" \
  -d "key=${TRELLO_API_KEY}" \
  -d "token=${TRELLO_TOKEN}" \
  -d "callbackURL=https://your-server.com/trello-webhook" \
  -d "idModel=${TRELLO_BOARD_ID}" \
  -d "description=VirtPLC Sync"
```

**2. Create Webhook Endpoint**

File: `.github/scripts/webhook-server.js`

```javascript
const express = require('express');
const app = express();

app.post('/trello-webhook', (req, res) => {
  const action = req.body.action;
  
  // When card moves to DONE list
  if (action.type === 'updateCard' && action.data.listAfter?.name === '✅ Sprint 3 - DONE') {
    // Update GitHub issue/PR status
    // Close related GitHub issue
    // Post celebration comment
  }
  
  res.sendStatus(200);
});

app.listen(3000);
```

---

## 🎯 Recommended Workflow

### Simple Setup (5 minutes):
1. ✅ Import CSV to Trello (Method 1 above)
2. ✅ Enable GitHub Power-Up on Trello
3. ✅ Use card URLs in commit messages

### Advanced Setup (30 minutes):
1. ✅ Import CSV to Trello
2. ✅ Setup GitHub Actions (Option B)
3. ✅ Configure secrets
4. ✅ Create automation rules

---

## 📝 Best Practices

### Commit Message Format
```bash
# Good - auto-links to Trello
git commit -m "feat: implement MCP tool calling https://trello.com/c/ABC123"
git commit -m "fix: resolve CORS issue #CORS-FIX"

# Better - includes context
git commit -m "feat(backend): implement MCP tool calling
- Add sensor data retrieval
- Implement auth and rate limiting
Trello: https://trello.com/c/ABC123"
```

### PR Description Template
```markdown
## Description
Brief description of changes

## Trello Card
https://trello.com/c/CARD_ID

## Checklist
- [ ] Tests added
- [ ] Documentation updated
- [ ] Trello card updated

## Related Issues
Closes #123
```

### Branch Naming
```bash
# Include card reference
git checkout -b feature/mcp-server-ABC123
git checkout -b fix/cors-issue-DEF456
git checkout -b sprint3/dashboard-builder-GHI789
```

---

## 🔧 Troubleshooting

### CSV Import Issues
**Problem:** Cards not importing
- **Solution:** Ensure lists are created before import
- **Solution:** Check CSV formatting (no special characters in list names)

**Problem:** Labels not appearing
- **Solution:** Create labels manually first, then import

### GitHub Power-Up Issues
**Problem:** Commits not showing on cards
- **Solution:** Use full Trello card URL in commit message
- **Solution:** Re-authorize GitHub Power-Up

### API Authentication Issues
**Problem:** 401 Unauthorized
- **Solution:** Regenerate Trello token
- **Solution:** Check API key is correct
- **Solution:** Verify token has read/write permissions

---

## 📊 Monitoring Sync Status

Create a status dashboard card that tracks:
- Last sync time
- Failed sync attempts
- Cards needing update
- Orphaned cards (no GitHub link)

---

## 🚀 Quick Start Commands

```bash
# 1. Import to Trello (manual step via UI)

# 2. Setup GitHub secrets
gh secret set TRELLO_API_KEY
gh secret set TRELLO_TOKEN  
gh secret set TRELLO_BOARD_ID

# 3. Test sync
git commit -m "test: trello sync https://trello.com/c/YOUR_CARD_ID"
git push

# 4. Verify in Trello card comments
```

---

**Need Help?** 
- Trello API Docs: https://developer.atlassian.com/cloud/trello/
- GitHub Actions: https://docs.github.com/en/actions
- Power-Ups Guide: https://developer.atlassian.com/cloud/trello/power-ups/
