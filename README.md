# Mining Operations Management System

## Introduction
The Mining Operations Management System is a comprehensive Django-based platform designed to streamline and manage all aspects of mining operations. It provides a centralized solution for production tracking, financial oversight, safety compliance, and company profile management across multiple mining operations.

## Features
### Core Functionality
- Multi-module architecture for different operational aspects
- Role-based access control for various user groups
- Comprehensive admin interface for managing records
- Audit logging with creation and update tracking
- File attachment handling for supporting documents
- State-based workflow transitions
- Multi-language support (Arabic/English)
- Automated reporting and data export

### Key Modules
1. **Production Tracking**
   - Gold movement and export management
   - Traditional mining operations tracking
   - Mineral production monitoring
   - Alloy tracking and weight calculations
   - Shipping documentation management

2. **Financial Management**
   - Revenue collection tracking
   - Fund distribution calculations
   - Financial reporting
   - Payment obligation monitoring
   - Local community obligations

3. **Safety & Compliance**
   - Incident reporting and tracking
   - Safety requirement compliance
   - Equipment and site inspections
   - Safety documentation management
   - Compliance reporting

4. **Company Management**
   - Company profile maintenance
   - License tracking and management
   - Application workflow management
   - Factory information tracking
   - User role and permission management

## Usage
To use the Mining Operations Management System:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Apply database migrations:
```bash
python manage.py migrate
```

3. Create initial user groups and permissions:
```bash
python manage.py create_app_groups
```

4. Start the development server:
```bash
python manage.py runserver
```

5. Access the admin interface at `/admin/` to manage records.

6. Use the following main user groups to control access:
   - production_manager
   - financial_controller
   - safety_officer
   - company_admin
   - state_representative
   - auditor

## User Workflows
The application implements the following workflows through the admin interface:

### Production Workflow
1. Create new production records
2. Track gold movement through states
3. Monitor traditional mining operations
4. Manage alloy tracking and calculations
5. Generate export documentation
6. Export data to CSV for reporting

### Financial Workflow
1. Record revenue collections
2. Track fund distributions
3. Generate financial reports
4. Monitor payment obligations
5. Manage local community obligations
6. Export financial data for analysis

### Safety Workflow
1. Report and track safety incidents
2. Monitor compliance requirements
3. Schedule and track equipment inspections
4. Manage safety documentation
5. Generate compliance reports
6. Export safety data for analysis

### Company Management Workflow
1. Create and maintain company profiles
2. Manage licenses and permits
3. Process various applications
4. Track application states and approvals
5. Manage factory information
6. Handle user roles and permissions

### Key Admin Features
- State-based record locking and permissions
- Automatic calculations and validations
- File attachment handling for supporting documents
- Audit trail tracking for all changes
- Custom admin views for each user group
- Date-based filtering with custom date ranges
- Module-specific record filtering
- Multi-language support in admin interface
- Automated report generation

### State Transitions
The system manages state transitions through the admin interface:
- Records start in DRAFT state
- Can be moved through approval states
- Can be canceled to CANCELED state
- Previous states are locked for editing
- Required data must be present before state transition
- Automatic email notifications for state changes
- Audit logging of all state transitions

### Security Features
- Role-based access control
- Module-specific data isolation
- File upload restrictions and validation
- Audit logging of all changes
- State-based permission enforcement
- Unique constraints on critical records
- Password policy enforcement
- Session timeout and security
