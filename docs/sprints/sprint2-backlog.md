# Sprint 2 Backlog Review – 2025.10.27-11.06

## Sprint Célok és Metrikák

**Sprint Időtartam:** 1.5 hét (október 27 - november 6, 2025)  
**Sprint Cél:** AI service route-ok befejezése, MCP szerver implementáció, dashboard komponensek fejlesztése, end-to-end adatfolyam kialakítása.  
**Definition of Done:** Kód committed, unit tesztek létrehozva és passing, integration tesztek sikeresek, dokumentáció frissítve, demo kész.

## Subteam-ek és Felelősségek

- **Backend Team (Spring Boot):** Júlia, Kristóf – MCP szerver implementáció, API endpoint-ok, adat aggregáció
- **AI Team (Python/FastAPI):** Nándi + AI érdeklődők – AI service route-ok, Ollama integráció, MCP kliens
- **Frontend Team (React):** Imelda, Norbi – Dashboard komponensek, WebSocket streaming, felhasználói interfész
- **DevOps Team (Docker/K8s):** Infrastruktúra setup, monitoring, deployment pipeline-ok
- **Data Team (TimeBase/PostgreSQL):** Séma implementáció, adat migráció, query optimalizálás

## Sprint Backlog Feladatok

### Backend Team (Júlia, Kristóf)

**Cél:** MCP szerver és adat aggregációs API-k befejezése

1. **MCP Server Endpoints Implementáció** (Story Points: 8)
   - Spring Boot MCP szerver létrehozása port 8000-on
   - Tool calling implementáció sensor adatokért, equipment státuszért, context retrievalért
   - Autentikáció és rate limiting hozzáadása
   - **Deliverable:** MCP kliens sikeresen hívhatja az összes tool-t

2. **Data Aggregation Service** (Story Points: 5)
   - REST API építése aggregált metrikákért TimeBase-ból
   - Caching implementáció Redis-szel
   - Adat export endpoint-ok hozzáadása
   - **Deliverable:** API aggregált adatokat ad vissza <500ms alatt

3. **Backend Dokumentáció** (Story Points: 3)
   - Összes API endpoint dokumentálása OpenAPI spec-kel
   - Integrációs guide MCP-hez
   - Architektúra diagramok frissítése
   - **Deliverable:** Docs elérhető /docs/api/ alatt

### AI Team (Nándi + AI érdeklődők)

**Cél:** AI service route-ok és integráció befejezése

1. **AI Service Routes Implementáció** (Story Points: 8)
   - Routes könyvtár létrehozása analysis.py, chat.py, dashboard.py fájlokkal (jelenleg nem létezik)
   - /api/analysis/analyze endpoint implementáció anomaly detection-höz
   - /api/chat endpoint hozzáadása MCP integrációval és WebSocket streaming-gel
   - /api/dashboard endpoint létrehozása komponens generáláshoz
   - **Deliverable:** Összes endpoint valid válaszokat ad megfelelő error handling-gal

2. **Ollama Integráció** (Story Points: 5)
   - Llama3 8B modell konfiguráció analysis task-okhoz
   - Prompt engineering implementáció factory adatokhoz
   - Modell performance monitoring hozzáadása
   - **Deliverable:** AI accurate insight-okat generál teszt adatokból

3. **TimeBase Integráció** (Story Points: 5)
   - Aktuális TimeBase kliens kapcsolat implementáció (stub replacement)
   - Adat ingestion és querying képességek hozzáadása
   - Time-series analysis függvények létrehozása
   - **Deliverable:** Sikeresen lehet olvasni/írni TimeBase stream-eket

4. **AI Service Dokumentáció** (Story Points: 3)
   - AI endpoint-ok és adat formátumok dokumentálása
   - Prompt template-ek guide-ja
   - MCP integrációs példák frissítése
   - **Deliverable:** Docs /docs/ai-service/ alatt

### Frontend Team (Imelda, Norbi)

**Cél:** Interaktív dashboard real-time update-ekkel

1. **Dashboard Component Library** (Story Points: 8)
   - Újrafelhasználható chart komponensek építése (Chart.js/React)
   - WebSocket kliens implementáció real-time data-ért AI service-ből
   - Komponens konfigurációs panel drag-and-drop-pal
   - Komponens típusok létrehozása: line chart, gauge, table, alert
   - **Deliverable:** 5 chart típus helyesen render-el real-time update-ekkel

2. **Chat Interface** (Story Points: 5)
   - Chat UI létrehozása message history-val
   - Integráció AI service WebSocket-kel (/api/chat)
   - File upload hozzáadása adat query-khez
   - Chat persistence implementáció (30 nap retention)
   - **Deliverable:** Felhasználók chat-elhetnek és AI válaszokat kaphatnak context-tel

3. **Dashboard Builder** (Story Points: 5)
   - Dashboard létrehozás/szerkesztés interface implementáció
   - Komponens library browser hozzáadása
   - Dashboard persistence PostgreSQL-be
   - Export funkcionalitás hozzáadása (PDF/CSV)
   - **Deliverable:** Felhasználók létrehozhatnak, menthetnek és megoszthatnak custom dashboard-okat

4. **Frontend Dokumentáció** (Story Points: 3)
   - Komponens API és használat dokumentálása
   - UI/UX guideline-ok létrehozása
   - User story-k frissítése screenshot-okkal
   - **Deliverable:** Docs /docs/frontend/ alatt

### DevOps Team

**Cél:** Production-ready infrastruktúra

1. **Docker Compose Optimalizálás** (Story Points: 5)
   - Health check-ek és resource limit-ek hozzáadása
   - Service discovery implementáció
   - Logging és monitoring konfiguráció (jelenleg nincs monitoring)
   - **Deliverable:** Összes service reliably indul

2. **CI/CD Pipeline** (Story Points: 8)
   - GitHub Actions setup build/test/deploy-hez (jelenleg nincs CI/CD)
   - Automatizált tesztelés hozzáadása minden service-hez
   - Blue-green deployment implementáció
   - **Deliverable:** Pipeline sikeresen deploy-ol staging-re

3. **Infrastructure Dokumentáció** (Story Points: 3)
   - Deployment procedúrák dokumentálása
   - Troubleshooting guide létrehozása
   - Docker setup instrukciók frissítése
   - **Deliverable:** Docs /docs/devops/ alatt

### Data Team

**Cél:** Adat storage és retrieval implementáció befejezése

1. **TimeBase Séma Implementáció** (Story Points: 5)
   - TimeBase stream-ek létrehozása és populálása teszt adatokkal
   - Adat ingestion pipeline OPC-UA-ból
   - Stream optimalizálás és indexing hozzáadása
   - **Deliverable:** Teszt adatok sikeresen load-olódnak és query-k működnek

2. **PostgreSQL Setup és Migráció** (Story Points: 5)
   - Adatbázis inicializálás összes séma-val (users, chat, dashboards)
   - Adat retention policy-k implementáció (30 nap chat-hez)
   - Backup és recovery procedúrák hozzáadása
   - **Deliverable:** Összes tábla létrehozva és populálva teszt adatokkal

3. **Data Pipeline Integráció** (Story Points: 5)
   - OPC-UA adatok csatlakoztatása TimeBase ingestion-höz
   - Adat aggregációs job-ok implementáció (1min, 5min, 1hour)
   - Adat validáció és quality check-ek hozzáadása
   - **Deliverable:** End-to-end adatfolyam szenzoroktól storage-ig

4. **Data Dokumentáció** (Story Points: 3)
   - Adatbázis sémák és relationship-ek dokumentálása
   - Adat flow diagramok létrehozása
   - Query optimalizálás guide-ok frissítése
   - **Deliverable:** Docs /docs/data/ alatt

## Sprint Metrikák és Célok

- **Velocity Target:** 92 story point (1.5 hét)
- **Quality Gate-ek:**
  - Unit test coverage: Establish basic test framework (target: >0%)
  - Integration tesztek: Implement basic integration tests
  - Performance benchmark-ok teljesítve (<2s latency, <500ms API response)
- **Risk-ek:** MCP integrációs komplexitás, TimeBase learning curve, route implementáció
- **Dependency-k:** Összes team befejezi dokumentációt sprint végéig

## Definition of Ready

- Feladatok estimated és assigned
- Acceptance kritériumok definiálva
- Nincs blocking external dependency
- Team megérti a requirement-eket

## Sprint Review Kritériumok

- Összes use case demonstrálható
- End-to-end adatfolyam működik
- Dokumentáció complete és reviewed
- Performance SLA-ket teljesít


## Sprint Backlog Tasks

### Backend Team Tasks

**Target:** Complete MCP server and data aggregation APIs

1. **Implement MCP Server Endpoints** (Story Points: 8)
   - Create Spring Boot MCP server at port 8000
   - Implement tool calling for sensor data, equipment status, context retrieval
   - Add authentication and rate limiting
   - **Assignee:** Backend Lead
   - **Acceptance:** MCP client can successfully call all tools

2. **Data Aggregation Service** (Story Points: 5)
   - Build REST API for aggregated metrics from TimeBase
   - Implement caching with Redis
   - Add data export endpoints
   - **Assignee:** Backend Developer
   - **Acceptance:** API returns aggregated data <500ms

3. **Backend Documentation** (Story Points: 3)
   - Document all API endpoints with OpenAPI spec
   - Create integration guide for MCP
   - Update architecture diagrams
   - **Assignee:** Backend Team
   - **Acceptance:** Docs accessible in /docs/api/

### AI Team Tasks

**Target:** Complete AI service routes and integration

1. **Implement AI Service Routes** (Story Points: 8)
   - Create routes directory with analysis.py, chat.py, dashboard.py
   - Implement /api/analysis/analyze endpoint for anomaly detection
   - Add /api/chat endpoint with MCP integration and WebSocket streaming
   - Create /api/dashboard endpoint for component generation
   - **Assignee:** AI Lead
   - **Acceptance:** All endpoints return valid responses with proper error handling

2. **Ollama Integration** (Story Points: 5)
   - Configure Llama3 8B model for analysis tasks
   - Implement prompt engineering for factory data
   - Add model performance monitoring
   - **Assignee:** AI Developer
   - **Acceptance:** AI generates accurate insights from test data

3. **TimeBase Integration** (Story Points: 5)
   - Aktuális TimeBase kliens connection implementáció (jelenleg mock/stub implementation)
   - Add data ingestion és querying képességek hozzáadása
   - Time-series analysis függvények létrehozása
   - **Assignee:** AI Developer
   - **Acceptance:** Can read/write TimeBase streams successfully

4. **AI Service Documentation** (Story Points: 3)
   - Document AI endpoints and data formats
   - Create prompt templates guide
   - Update MCP integration examples
   - **Assignee:** AI Team
   - **Acceptance:** Docs in /docs/ai-service/

### Frontend Team Tasks

**Target:** Build interactive dashboard with real-time updates

1. **Dashboard Component Library** (Story Points: 8)
   - Build reusable chart components (Chart.js/React)
   - Implement WebSocket client for real-time data from AI service
   - Add component configuration panel with drag-and-drop
   - Create component types: line chart, gauge, table, alert
   - **Assignee:** Frontend Lead
   - **Acceptance:** 5 chart types render correctly with real-time updates

2. **Chat Interface** (Story Points: 5)
   - Create chat UI with message history
   - Integrate with AI service WebSocket (/api/chat)
   - Add file upload for data queries
   - Implement chat persistence (30 days retention)
   - **Assignee:** Frontend Developer
   - **Acceptance:** Users can chat and receive AI responses with context

3. **Dashboard Builder** (Story Points: 5)
   - Implement dashboard creation/editing interface
   - Add component library browser
   - Create dashboard persistence to PostgreSQL
   - Add export functionality (PDF/CSV)
   - **Assignee:** Frontend Developer
   - **Acceptance:** Users can create, save, and share custom dashboards

4. **Frontend Documentation** (Story Points: 3)
   - Document component API and usage
   - Create UI/UX guidelines
   - Update user stories with screenshots
   - **Assignee:** Frontend Team
   - **Acceptance:** Docs in /docs/frontend/

### DevOps Team Tasks

**Target:** Production-ready infrastructure

1. **Docker Compose Optimization** (Story Points: 5)
   - Add health checks and resource limits
   - Implement service discovery
   - Configure logging and monitoring
   - **Assignee:** DevOps Lead
   - **Acceptance:** All services start reliably

2. **CI/CD Pipeline** (Story Points: 8)
   - GitHub Actions setup build/test/deploy-hez (jelenleg nincs CI/CD)
   - Automatizált tesztelés hozzáadása minden service-hez
   - Blue-green deployment implementáció
   - **Assignee:** DevOps Developer
   - **Acceptance:** Pipeline sikeresen deploy-ol staging-re

3. **Infrastructure Documentation** (Story Points: 3)
   - Document deployment procedures
   - Create troubleshooting guide
   - Update Docker setup instructions
   - **Assignee:** DevOps Team
   - **Acceptance:** Docs in /docs/devops/

### Data Team Tasks

**Target:** Complete data storage and retrieval implementation

1. **TimeBase Schema Implementation** (Story Points: 5)
   - Create and populate TimeBase streams with test data
   - Implement data ingestion pipeline from OPC-UA
   - Add stream optimization and indexing
   - **Assignee:** Data Lead
   - **Acceptance:** Test data loads successfully and queries work

2. **PostgreSQL Setup and Migration** (Story Points: 5)
   - Initialize database with all schemas (users, chat, dashboards)
   - Implement data retention policies (30 days for chat)
   - Add backup and recovery procedures
   - **Assignee:** Data Developer
   - **Acceptance:** All tables created and populated with test data

3. **Data Pipeline Integration** (Story Points: 5)
   - Connect OPC-UA data to TimeBase ingestion
   - Implement data aggregation jobs (1min, 5min, 1hour)
   - Add data validation and quality checks
   - **Assignee:** Data Developer
   - **Acceptance:** End-to-end data flow from sensors to storage

4. **Data Documentation** (Story Points: 3)
   - Document database schemas and relationships
   - Create data flow diagrams
   - Update query optimization guides
   - **Assignee:** Data Team
   - **Acceptance:** Docs in /docs/data/
