# 🚀 Quick Trello Setup - 5 Minutes

## Step 1: Import CSV to Trello (2 min)

1. Go to [trello.com](https://trello.com) and create board: **VirtPLC SCRUM Board**

2. Create these 7 lists (in order):
   - `📋 Backlog`
   - `🎯 Sprint 3 - TODO`  
   - `🔄 Sprint 3 - IN PROGRESS`
   - `🔴 BLOCKED`
   - `✅ Sprint 3 - DONE`
   - `📦 Sprint 2 - DONE`
   - `🏆 Sprint 1 - DONE`

3. Board Menu → More → Print and export → **Import**
   - Upload: `.github/trello-import.csv`
   - Click Import

## Step 2: Get Trello Credentials (2 min)

1. **Get API Key:**
   - Visit: https://trello.com/power-ups/admin
   - Click "New" → "Create" (or use existing)
   - Copy your API Key

2. **Get Token:**
   - Visit: `https://trello.com/1/authorize?key=YOUR_API_KEY&name=VirtPLC&expiration=never&response_type=token&scope=read,write`
   - Replace `YOUR_API_KEY` with your key
   - Click "Allow"
   - Copy the token

3. **Get List IDs:**
   - Open your board
   - Add `.json` to URL: `https://trello.com/b/BOARD_ID.json`
   - Find list IDs:
     - Search for `"name":"✅ Sprint 3 - DONE"` → copy its `id`
     - Optional: Get other list IDs if needed

## Step 3: Add GitHub Secrets (1 min)

1. Go to: `https://github.com/Dedzsinator/VirtPLC/settings/secrets/actions`

2. Click "New repository secret" for each:
   ```
   Name: TRELLO_API_KEY
   Value: <your-api-key>
   
   Name: TRELLO_TOKEN
   Value: <your-token>
   
   Name: TRELLO_DONE_LIST_ID
   Value: <done-list-id>
   ```

## ✅ Done! Now it works automatically:

### When you commit:
```bash
git commit -m "fix: resolve CORS https://trello.com/c/CARD_ID"
git push
```
→ Comment appears on Trello card with commit details

### When you create PR:
```
Title: "Implement MCP Server https://trello.com/c/CARD_ID"
```
→ Comment appears on Trello card

### When PR is merged:
→ Card automatically moves to "Sprint 3 - DONE" list

---

## 🎯 Usage Examples

### In commits:
```bash
# Full URL
git commit -m "feat: add WebSocket streaming https://trello.com/c/abc123XYZ"

# Short reference  
git commit -m "fix: CORS issue #abc123XYZ"
```

### In PR title or description:
```markdown
## Implements MCP Tool Calling

Trello: https://trello.com/c/abc123XYZ

- [x] Sensor data retrieval
- [x] Auth and rate limiting
```

---

## 📋 Bonus: GitHub Power-Up (Optional)

For even better integration:

1. Open Trello board
2. Power-Ups → Search "GitHub"
3. Add official GitHub Power-Up
4. Authorize with your GitHub account
5. Connect to repository: `Dedzsinator/VirtPLC`

Now GitHub commits/PRs show directly on Trello cards!

---

## 🔍 Verify It's Working

1. Make a test commit with Trello card URL
2. Check GitHub Actions: `https://github.com/Dedzsinator/VirtPLC/actions`
3. Look for "Trello Card Sync" workflow
4. Check Trello card for comment

---

**Questions?** See full guide: `.github/TRELLO_SYNC_GUIDE.md`
