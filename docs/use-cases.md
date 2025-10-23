# VirtPLC Use Cases és Acceptance Kritériumok

## Elsődleges Use Case-ek

### UC-1: Real-Time Factory Monitoring

**Leírás:** Operátorok élő szenzor adatokat és equipment státuszt nézhetnek interaktív dashboard-okon keresztül.  
**Actors:** Warehouse Operator, Operations Manager  
**Preconditions:** Szenzorok csatlakoztatva, TimeBase fut  
**Postconditions:** Real-time data megjelenítve <2s latency-val  

**Acceptance Kritériumok:**

- Dashboard élő metrikákat mutat TimeBase stream-ekből
- WebSocket update minden 1 másodpercben
- Alert notification-ok threshold breach-eknél
- Historical data elérhető utolsó 30 napra

### UC-2: AI-Powered Anomaly Detection

**Leírás:** AI elemzi szenzor pattern-eket anomaly-k detektálására és issue-k prediktálására.  
**Actors:** AI System, Maintenance Technician  
**Preconditions:** Historical data elérhető, Ollama modell betöltve  
**Postconditions:** Anomaly-k flagged confidence score-okkal  

**Acceptance Kritériumok:**

- AI feldolgozza factory_metrics stream adatokat
- Anomaly detection accuracy >85% teszt adatokon
- Prediction-ok tárolva ai_predictions stream-ben
- Alert-ek küldve MCP-n keresztül backend-nek

### UC-3: Natural Language Chat with AI

**Leírás:** Felhasználók természetes nyelvvel query-zik a rendszerrel insight-okért és analysis-ért.  
**Actors:** Operations Manager, Administrator  
**Preconditions:** MCP kapcsolat established, chat history tárolva  
**Postconditions:** Kontextuális válaszok data vizualizációkkal  

**Acceptance Kritériumok:**

- Chat interface elfogad természetes nyelv query-ket
- AI MCP tool-okat használ relevant data retrieval-hez
- Válaszok tartalmaznak chart-okat/table-okat dashboard komponensekből
- Conversation history retained 30 napra (konfigurálható)

### UC-4: Custom Dashboard Creation

**Leírás:** Felhasználók személyre szabott dashboard-okat hoznak létre drag-and-drop komponensekkel.  
**Actors:** Operations Manager, Administrator  
**Preconditions:** Komponens library elérhető, user permission-ok beállítva  
**Postconditions:** Dashboard-ok mentve és share-elhetők  

**Acceptance Kritériumok:**

- 5+ chart típus elérhető (line, bar, gauge, table)
- Komponensek konfigurálhatók data source-okkal
- Dashboard-ok persist PostgreSQL-ben
- Export funkcionalitás PDF/CSV-hez

### UC-5: Predictive Maintenance Alerts

**Leírás:** Rendszer prediktálja equipment failure-eket és ütemez maintenance-et.  
**Actors:** Maintenance Technician, AI System  
**Preconditions:** Equipment szenzor data streaming, AI modellek trained  
**Postconditions:** Maintenance task-ok auto-generated  

**Acceptance Kritériumok:**

- Prediction-ok time-series analysis alapján
- Alert-ek küldve 24-48 órával predicted failure előtt
- Maintenance log-ok frissítve chat interface-en keresztül
- False positive rate <10%

## Támogató Use Case-ek

- **User Authentication & Role Management:** JWT-based auth user/admin role-okkal
- **Chat History Persistence:** 30 nap konfigurálható retention conversation-ökhöz
- **Dashboard Component Generation:** AI készít React komponenseket user prompt-okból
- **Data Export & Reporting:** PDF/CSV export funkcionalitás dashboard-okhoz
- **Real-time WebSocket Streaming:** Live data update-ek minden komponensben
