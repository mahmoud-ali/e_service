# Mining Operations Planning & Reporting System

A comprehensive platform for managing mineral production, safety compliance, and financial tracking in mining operations.

## Key Features

### Core Functionality
- Annual goal hierarchy (Goals > Sub-Goals > Departmental Tasks)
- Monthly plan vs actual performance tracking
- Production monitoring (Gold, Minerals, Traditional Mining)
- Financial collection planning & distribution tracking
- Safety incident reporting & compliance monitoring

### Reporting Modules
- **Production Tracking**
  - Company & traditional mining outputs
  - Mineral production by type/weight
  - Gold export documentation
- **Safety Management**
  - Accident/incident reporting
  - Safety requirement compliance
  - Equipment & site inspections
- **Financial Oversight**
  - Revenue collection by category
  - Fund distribution tracking
  - Local community obligations
- **Ancillary Services**
  - Media monitoring (TV/radio/digital)
  - IT support request tracking
  - Legal case management

### Technical Highlights
- Multi-lingual UI (Arabic/English)
- Configurable workflow states (Draft/Confirmed)
- Audit trails for all data changes
- Role-based access control
- Automated progress calculations
- Data import/export capabilities

## Data Model Overview
```mermaid
classDiagram
    Goal <|-- Task
    Task --> TaskDuration
    YearlyPlanning --> CompanyProductionMonthlyPlanning
    YearlyPlanning --> TraditionaProductionMonthlyPlanning
    MonthelyReport --> TaskExecution
    TaskExecution --> TaskExecutionDetail
    TaskExecutionDetail <|-- CompanyProductionTask
    TaskExecutionDetail <|-- Traditional7oadthTask
    TaskExecutionDetail <|-- MediaITSupportTask
    
    class Goal {
        +String code
        +String name
        +String outcome
        +String kpi
    }
    
    class TaskExecution {
        +Int percentage
        +String problems
        +DateTime created_at
    }
