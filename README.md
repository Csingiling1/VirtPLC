# VirtPLC - PLC + HMI Control System

An Accenture Challenge - Control & Visualization Subteam

## Branch: feature/HMI

This branch contains the Ignition Edge HMI dashboard and PLC control logic for the virtual factory.

## Overview

Industrial control dashboard providing real-time monitoring, control, and data logging for factory equipment via OPC-UA.

## Project Structure

```
IgnitionEdge/          # Ignition Edge Gateway files
├── config/            # Gateway configuration
├── projects/          # HMI projects
└── tags/              # Tag definitions

PLCLogic/              # PLC control logic
├── ladder/            # Ladder logic files
└── structured/        # Structured text programs

TimeBaseDB/            # TimeBaseDB configuration
└── config/            # Database and retention policies

Docs/                  # Documentation
├── Setup.md           # Installation guide
├── HMI-Design.md      # HMI layout specifications
├── Tag-Configuration.md  # Tag definitions
└── Integration.md     # Backend integration guide
```

## Quick Start

1. Install Ignition Edge (maker.inductiveautomation.com)
2. Follow `Docs/Setup.md` for configuration
3. Import HMI project from `IgnitionEdge/projects/`
4. Configure OPC-UA connection to `opc.tcp://backend:4840`
5. Start TimeBaseDB and configure historian

## Features

- Real-time equipment monitoring dashboards
- Interactive control panels (Start/Stop/Reset)
- Live data visualization with charts
- Alarm and fault management
- Historical data trending with TimeBaseDB
- OPC-UA tag synchronization

## Documentation

- **Setup.md** - Installation and configuration steps
- **HMI-Design.md** - Dashboard layout and components
- **Tag-Configuration.md** - Complete tag definitions
- **Integration.md** - Backend and database integration
