# VirtPLC Trello Board Integration

## 🔗 Trello Board Link

**Main Project Board:** [VirtPLC SCRUM Board](https://trello.com/b/YOUR_BOARD_ID/virtplc-scrum)

> **Note:** Replace `YOUR_BOARD_ID` with your actual Trello board ID after creating the board.

---

## 📋 Quick Setup Instructions

### 1. Create Trello Board

1. Go to [Trello](https://trello.com)
2. Click "Create new board"
3. Name it: **VirtPLC SCRUM Board**
4. Set visibility to your preference (Team/Private)

### 2. Create Lists (Columns)

Create these lists in order:
1. **📋 Backlog**
2. **🎯 Sprint 3 - TODO**
3. **🔄 Sprint 3 - IN PROGRESS**
4. **🔴 BLOCKED**
5. **✅ Sprint 3 - DONE**
6. **📦 Sprint 2 - DONE**
7. **🏆 Sprint 1 - DONE**

### 3. Set Up Labels

Create these labels for categorization:

| Label | Color | Usage |
|-------|-------|-------|
| `Backend` | Blue | Backend team tasks |
| `Frontend` | Green | Frontend team tasks |
| `AI Service` | Purple | AI/ML tasks |
| `DevOps` | Orange | Infrastructure tasks |
| `Data` | Yellow | Data pipeline tasks |
| `P0-Critical` | Red | Critical priority |
| `P1-High` | Orange | High priority |
| `P2-Medium` | Yellow | Medium priority |
| `P3-Low` | Green | Low priority |
| `Bug` | Red | Bug fixes |
| `Feature` | Blue | New features |
| `Tech Debt` | Black | Technical debt |

### 4. Import Cards

Use the CSV import method or create cards manually using the structure below.

---

## 📊 Trello Board Structure

### List: 🎯 Sprint 3 - TODO

#### Card: MCP Server Completion
- **Description:** Complete tool calling implementation for sensor data retrieval
- **Story Points:** 8
- **Labels:** Backend, P0-Critical, Feature
- **Assignees:** Júlia, Kristóf
- **Due Date:** Nov 18, 2025
- **Checklist:**
  - [ ] Implement sensor data retrieval
  - [ ] Add equipment status queries
  - [ ] Context retrieval for LLM
  - [ ] Authentication and rate limiting
  - [ ] Error handling and logging
  - [ ] Performance testing (<100ms)
- **Files:** `backend/src/main/java/com/virtplc/mcp/`

#### Card: WebSocket Implementation
- **Description:** Real-time data streaming endpoints
- **Story Points:** 5
- **Labels:** Backend, P0-Critical, Feature
- **Assignees:** Júlia, Kristóf
- **Due Date:** Nov 19, 2025
- **Dependencies:** MCP Server Completion
- **Checklist:**
  - [ ] Real-time data streaming endpoints
  - [ ] Connection management
  - [ ] Message queuing system
  - [ ] Handle 1000+ concurrent connections
  - [ ] Reconnection logic
- **Files:** `backend/src/main/java/com/virtplc/streaming/`

#### Card: Dashboard Builder
- **Description:** Drag-and-drop dashboard creation interface
- **Story Points:** 8
- **Labels:** Frontend, P0-Critical, Feature
- **Assignees:** Imelda, Norbi
- **Due Date:** Nov 20, 2025
- **Checklist:**
  - [ ] Drag-and-drop interface
  - [ ] Component library browser
  - [ ] PostgreSQL persistence
  - [ ] PDF/CSV/JSON export
  - [ ] Template system
  - [ ] Target: <5 min dashboard creation
- **Files:** `frontend/src/pages/Dashboard.tsx`

#### Card: Real-time AI Streaming
- **Description:** WebSocket streaming for AI chat
- **Story Points:** 8
- **Labels:** AI Service, P0-Critical, Feature
- **Assignees:** Nándi + AI Team
- **Due Date:** Nov 19, 2025
- **Checklist:**
  - [ ] WebSocket streaming for /api/chat
  - [ ] Token processing optimization
  - [ ] Context management
  - [ ] Target: <500ms latency
  - [ ] Fix httpx dependency issue
- **Files:** `ai-service/src/routes/chat.py`

#### Card: Unit Testing Framework
- **Description:** Setup testing framework across all services
- **Story Points:** 12
- **Labels:** DevOps, P0-Critical, Tech Debt
- **Assignees:** All Teams
- **Due Date:** Nov 21, 2025
- **Checklist:**
  - [ ] Backend: JUnit tests (>80% coverage)
  - [ ] AI Service: Pytest tests
  - [ ] Frontend: Jest/React Testing Library
  - [ ] Integration tests
  - [ ] Load testing
  - [ ] E2E workflow tests
- **Target:** 80%+ coverage

#### Card: CI/CD Pipeline
- **Description:** GitHub Actions implementation
- **Story Points:** 8
- **Labels:** DevOps, P1-High, Feature
- **Assignees:** DevOps Team
- **Due Date:** Nov 21, 2025
- **Checklist:**
  - [ ] GitHub Actions workflow
  - [ ] Automated testing
  - [ ] Blue-green deployment
  - [ ] Rollback capabilities
  - [ ] Docker image builds
- **Files:** `.github/workflows/`

#### Card: Monitoring Stack
- **Description:** Prometheus + Grafana observability
- **Story Points:** 5
- **Labels:** DevOps, P1-High, Feature
- **Assignees:** DevOps Team
- **Due Date:** Nov 20, 2025
- **Checklist:**
  - [ ] Prometheus metrics collection
  - [ ] Grafana dashboards
  - [ ] ELK centralized logging
  - [ ] Alert system
  - [ ] Service health monitoring

---

### List: 🔄 Sprint 3 - IN PROGRESS

#### Card: Frontend Login CORS Fix
- **Description:** Resolve browser login authentication issue
- **Story Points:** 2
- **Labels:** Frontend, Backend, P0-Critical, Bug
- **Assignees:** Investigation Team
- **Status:** 🟡 Investigating
- **Checklist:**
  - [x] Verified curl login works
  - [x] Checked CORS configuration
  - [x] Verified API base URL
  - [ ] Debug browser console errors
  - [ ] Test with different browsers
  - [ ] Verify frontend container network
- **Files:** `docker-compose.yml`, `frontend/.env`, `backend/src/main/java/com/virtplc/config/CorsConfig.java`

---

### List: 🔴 BLOCKED

#### Card: WebSocket Client Implementation
- **Description:** Frontend WebSocket client for real-time updates
- **Story Points:** 5
- **Labels:** Frontend, P0-Critical, Feature
- **Blocked By:** Backend WebSocket Implementation
- **Checklist:**
  - [ ] AI service WebSocket integration
  - [ ] Real-time chart updates
  - [ ] Reconnection logic
  - [ ] Error handling
- **Files:** `frontend/src/`

#### Card: Advanced AI Features
- **Description:** Predictive analytics and anomaly detection
- **Story Points:** 5
- **Labels:** AI Service, P1-High, Feature
- **Blocked By:** TimeBase Advanced Integration
- **Checklist:**
  - [ ] Predictive analytics for time-series
  - [ ] Enhanced anomaly detection
  - [ ] Multi-modal AI responses
  - [ ] Chart suggestion engine

---

### List: ✅ Sprint 3 - DONE

#### Card: OPC-UA Direct Streaming
- **Description:** Go collector with TimescaleDB ingestion
- **Story Points:** 5
- **Labels:** Data, Feature
- **Completed:** Nov 12, 2025
- **Achievements:**
  - ✅ Go collector implementation
  - ✅ Direct TimescaleDB ingestion
  - ✅ 12 sensors reading
  - ✅ 45,000+ records collected
  - ✅ Real-time data streaming
- **Files:** `collector/main.go`

---

### List: 📦 Sprint 2 - DONE

#### Card: AI-Powered Chart System
- **Description:** Multi-library chart generation system
- **Story Points:** 18
- **Labels:** AI Service, Frontend, Feature
- **Completed:** Nov 6, 2025
- **Achievements:**
  - ✅ Recharts + Chart.js integration
  - ✅ React component generation
  - ✅ PNG export functionality
  - ✅ Live code editing
  - ✅ Security measures (XSS prevention)
- **Files:** `ai-service/src/routes/chart.py`, `frontend/src/components/AIChart.tsx`

#### Card: Backend Stability Fixes
- **Description:** Hibernate and CORS fixes
- **Story Points:** 8
- **Labels:** Backend, Bug, Tech Debt
- **Completed:** Nov 5, 2025
- **Achievements:**
  - ✅ LazyInitializationException fix
  - ✅ CORS preflight handling
  - ✅ Multi-origin support
- **Files:** `backend/src/main/java/com/virtplc/`

---

### List: 🏆 Sprint 1 - DONE

#### Card: Microservices Architecture
- **Description:** Complete system architecture design
- **Story Points:** 15
- **Labels:** DevOps, Feature
- **Completed:** Oct 23, 2025
- **Achievements:**
  - ✅ Architecture documentation
  - ✅ Technology stack selection
  - ✅ Database schema design
  - ✅ Docker orchestration
- **Files:** `docs/`, `docker-compose.yml`

#### Card: Backend Foundation
- **Description:** Spring Boot setup with JWT auth
- **Story Points:** 12
- **Labels:** Backend, Feature
- **Completed:** Oct 22, 2025
- **Achievements:**
  - ✅ REST API implementation
  - ✅ JWT authentication
  - ✅ Database integration
  - ✅ Health endpoints
- **Files:** `backend/src/main/java/com/virtplc/`

#### Card: Frontend Foundation
- **Description:** React TypeScript setup
- **Story Points:** 8
- **Labels:** Frontend, Feature
- **Completed:** Oct 21, 2025
- **Achievements:**
  - ✅ Vite + TypeScript setup
  - ✅ shadcn/ui integration
  - ✅ Routing configuration
  - ✅ Component structure
- **Files:** `frontend/src/`

---

### List: 📋 Backlog

#### Card: Production Deployment
- **Description:** Kubernetes deployment preparation
- **Story Points:** 5
- **Labels:** DevOps, P1-High, Feature
- **Checklist:**
  - [ ] Kubernetes manifests
  - [ ] Database migration strategies
  - [ ] Security hardening
  - [ ] Load balancer configuration
- **Files:** `kubernetes/`, `infra/`

#### Card: Advanced UI Components
- **Description:** Gauge, KPI, Alert components
- **Story Points:** 5
- **Labels:** Frontend, P2-Medium, Feature
- **Checklist:**
  - [ ] Gauge components
  - [ ] KPI indicators
  - [ ] Alert/notification system
  - [ ] Advanced table components

#### Card: Security Vulnerability Fixes
- **Description:** Fix Golang base image vulnerabilities
- **Story Points:** 2
- **Labels:** DevOps, P1-High, Bug
- **Issue:** 5 high vulnerabilities in collector/Dockerfile
- **Files:** `collector/Dockerfile`

#### Card: Advanced Analytics
- **Description:** TimeBase advanced time-series functions
- **Story Points:** 8
- **Labels:** Data, P2-Medium, Feature
- **Checklist:**
  - [ ] Complex time-series analysis
  - [ ] Predictive modeling integration
  - [ ] Advanced aggregations
  - [ ] Windowing functions

#### Card: Backup & Recovery System
- **Description:** Automated backup strategy
- **Story Points:** 3
- **Labels:** DevOps, Data, P1-High, Feature
- **Checklist:**
  - [ ] Automated backup for TimeBase & PostgreSQL
  - [ ] Point-in-time recovery
  - [ ] Disaster recovery procedures
  - [ ] Target: <1h RTO, <1 day RPO

---

## 🔧 Trello Power-Ups Recommendations

Enable these Power-Ups to enhance your board:

1. **Custom Fields** - Add Story Points, Team, Status fields
2. **Calendar** - View due dates in calendar format
3. **Card Aging** - Highlight stale cards
4. **GitHub** - Link commits and PRs to cards
5. **Burndown Chart** - Track sprint progress
6. **Voting** - Team prioritization
7. **Slack** - Notifications to team channel

---

## 📱 Trello Mobile Setup

1. Download Trello mobile app (iOS/Android)
2. Enable push notifications for:
   - Card assignments
   - Due date reminders
   - Comments and mentions
   - Card movements

---

## 🤖 Automation Rules

Set up these Butler automations:

```
When a card is moved to "Sprint 3 - DONE", 
  add the green "Completed" label and 
  set due date to today

When a card with "P0-Critical" label is added,
  move to top of list and
  send notification to @team

When due date is approaching in 2 days,
  add yellow "Due Soon" label and
  comment "@assignees This card is due in 2 days"

Every Monday at 9:00 AM,
  post comment "🚀 Sprint 3 Week {weeknumber}" to "Sprint Status" card
```

---

## 📊 Reporting & Metrics

### Weekly Sprint Review Template

Copy this card template each week:

**Card: Sprint 3 - Week {N} Review**
- Velocity: X story points completed
- Completion: Y% of sprint
- Blockers: List active blockers
- Risks: Identify risks
- Next week focus: Top 3 priorities

---

## 🔗 Quick Links

- **GitHub Repository:** https://github.com/Dedzsinator/VirtPLC
- **Documentation:** `docs/SCRUM_BOARD.md`
- **Sprint Backlogs:** `docs/sprints/`
- **Deployment Guide:** `docs/deployment/`

---

## 📝 Board Maintenance

### Daily Standup Checklist
- [ ] Move completed cards to DONE
- [ ] Update IN PROGRESS cards with comments
- [ ] Identify new blockers
- [ ] Adjust priorities based on dependencies

### Sprint Planning Checklist
- [ ] Review backlog and prioritize
- [ ] Assign story points to new cards
- [ ] Set due dates for sprint
- [ ] Assign team members
- [ ] Clear previous sprint DONE list

### Sprint Retrospective
- [ ] Move all sprint cards to appropriate DONE list
- [ ] Calculate velocity
- [ ] Document lessons learned
- [ ] Update backlog priorities
- [ ] Plan next sprint

---

## 🎯 Success Metrics

Track these KPIs on your board:

- **Sprint Velocity:** Story points completed per week
- **Cycle Time:** Days from TODO → DONE
- **Blocked Rate:** % of cards blocked
- **Team Load:** Cards per team member
- **Priority Distribution:** % P0/P1/P2/P3

---

**Last Updated:** November 14, 2025  
**Maintained By:** VirtPLC Team  
**Questions?** Create a card in the "Questions" list or mention @team
