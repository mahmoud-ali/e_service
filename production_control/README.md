# Production Control Django Application

## Introduction
The Production Control application is a Django-based system designed to manage and track gold production and shipping processes. It provides a structured approach to handling production forms, alloy tracking, and shipping documentation.

## Features
1. Gold production form management
2. Alloy tracking and weight calculations
3. Gold shipping form management
4. Role-based access control for different user groups
5. Comprehensive admin interface for managing records
6. Audit logging with creation and update tracking
7. File attachment handling for supporting documents
8. State-based workflow transitions
9. Automatic form numbering and state code generation
10. CSV export functionality for transaction data

## Usage
To use the Production Control application:

1. Ensure all migrations are applied:
```bash
python manage.py migrate
```

2. Create user groups and assign permissions using the admin interface.

3. Access the admin interface at `/admin/production_control/` to manage records.

4. Use the following main user groups to control access:
   - production_control_auditor
   - production_control_auditor_distributor
   - pro_company_application_accept
   - pro_company_application_approve

## User Workflows
The application implements the following workflows through the admin interface:

### Production Workflow
1. Create new gold production forms with:
   - Company details
   - Production date
   - Form number
   - Alloy details (serial numbers, weights, added gold)
2. Process forms through state transitions:
   - DRAFT
   - CONFIRMED
   - APPROVED
3. Generate production reports
4. Export data to CSV for reporting

### Shipping Workflow
1. Create new gold shipping forms with:
   - Company details
   - Shipping date
   - Form number
   - Alloy serial numbers
2. Process forms through state transitions:
   - DRAFT
   - CONFIRMED
   - APPROVED
3. Generate shipping certificates
4. Export data to CSV for reporting

### Key Admin Features
1. State-based form locking and permissions
2. Automatic form numbering with state codes
3. File attachment handling for supporting documents
4. Audit trail tracking for all changes
5. Custom admin views for each user group
6. Date-based filtering with custom date ranges
7. Company-specific form filtering

### State Transitions
The system manages state transitions through the admin interface:
1. Forms start in DRAFT state
2. Can be moved through approval states
3. Previous states are locked for editing
4. Required data must be present before state transition
5. Notifications and logging for state changes

### Security Features
1. Role-based access control
2. Company-specific data isolation
3. File upload restrictions
4. Audit logging of all changes
5. State-based permission enforcement
6. Unique constraints on critical records
