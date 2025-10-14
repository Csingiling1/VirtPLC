# Use Case Diagram

This diagram illustrates the key interactions between system actors and the AI-Driven Digital Twin platform.

```plantuml
@startuml
title AI-Driven Digital Twin - Use Case Diagram

actor "Warehouse Operator" as Operator
actor "Maintenance Technician" as Technician
actor "Operations Manager" as Manager
actor "Administrator" as Admin
actor "AI Engine" as AI

rectangle "Digital Twin System" {
    usecase "Scan & Segment Environment" as UC1
    usecase "Monitor Real-Time Data" as UC2
    usecase "Predict Maintenance" as UC3
    usecase "Control Equipment via PLC" as UC4
    usecase "Generate Reports" as UC5
    usecase "Query System via Natural Language" as UC6
    usecase "Manage Users & Configuration" as UC7
}

Operator --> UC2
Technician --> UC4
Technician --> UC3
Manager --> UC5
Manager --> UC6
Admin --> UC7
AI --> UC1
AI --> UC3

@enduml
```

## Actor Descriptions

**Warehouse Operator:** Monitors real-time data from warehouse sensors and equipment.

**Maintenance Technician:** Controls PLC-connected machinery and schedules maintenance activities.

**Operations Manager:** Views performance metrics, generates reports, and queries the system.

**Administrator:** Manages system configuration, user access, and infrastructure.

**AI Engine:** Performs automated environment scanning, segmentation, and predictive analysis.

## Use Case Descriptions

- **UC1 - Scan & Segment Environment:** Automated spatial mapping and object detection
- **UC2 - Monitor Real-Time Data:** Live viewing of sensor and equipment status
- **UC3 - Predict Maintenance:** AI-driven predictive analysis for equipment maintenance
- **UC4 - Control Equipment via PLC:** Direct control of warehouse machinery and systems
- **UC5 - Generate Reports:** Creation of performance and operational reports
- **UC6 - Query System via Natural Language:** Natural language interface for system queries
- **UC7 - Manage Users & Configuration:** System administration and configuration management
