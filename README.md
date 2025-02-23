# Mining Operations Management System

## Introduction
The Mining Operations Management System is a comprehensive Django-based platform designed to streamline and manage all aspects of mining operations, including production tracking, financial oversight, safety compliance, and company profile management.

## Features
### Core Functionality
- Multi-module architecture for different operational aspects
- Role-based access control for various user groups
- Comprehensive admin interface for managing records
- Audit logging with creation and update tracking
- File attachment handling for supporting documents
- State-based workflow transitions

### Key Modules
1. **Production Tracking**
   - Gold movement and export management
   - Traditional mining operations tracking
   - Mineral production monitoring
2. **Financial Management**
   - Revenue collection tracking
   - Fund distribution calculations
   - Financial reporting
3. **Safety & Compliance**
   - Incident reporting
   - Safety requirement tracking
   - Equipment inspections
4. **Company Management**
   - Company profile maintenance
   - License tracking
   - Application workflow management

## Usage
To use the Mining Operations Management System:

1. Ensure all migrations are applied:
```bash
python manage.py migrate
```

2. Create user groups and assign permissions using the admin interface.

3. Access the admin interface at `/admin/` to manage records.


## User Workflows
The application implements the following workflows through the admin interface:

### Production Workflow
1. Create new production records
2. Track gold movement through states
3. Monitor traditional mining operations
4. Generate export documentation
5. Export data to CSV for reporting

### Financial Workflow
1. Record revenue collections
2. Track fund distributions
3. Generate financial reports
4. Monitor payment obligations

### Safety Workflow
1. Report safety incidents
2. Track compliance requirements
3. Schedule equipment inspections
4. Generate safety reports

### Company Management Workflow
1. Create and maintain company profiles
2. Manage licenses and permits
3. Process various applications
4. Track application states and approvals

### Key Admin Features
- State-based record locking and permissions
- Automatic calculations and validations
- File attachment handling for supporting documents
- Audit trail tracking for all changes
- Custom admin views for each user group
- Date-based filtering with custom date ranges
- Module-specific record filtering

### State Transitions
The system manages state transitions through the admin interface:
- Records start in DRAFT state
- Can be moved through approval states
- Can be canceled to CANCELED state
- Previous states are locked for editing
- Required data must be present before state transition
- Notifications and logging for state changes

### Security Features
- Role-based access control
- Module-specific data isolation
- File upload restrictions
- Audit logging of all changes
- State-based permission enforcement
- Unique constraints on critical records
