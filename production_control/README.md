# Production Control Django Application

## Introduction
The Production Control application is a Django-based system designed to manage and track gold production and shipping processes. It provides a structured approach to handling production forms, alloy tracking, and shipping documentation.

## Features
- Gold production form management
- Alloy tracking and weight calculations
- Gold shipping form management
- Role-based access control for different user groups
- Comprehensive admin interface for managing records
- Audit logging with creation and update tracking
- File attachment handling for supporting documents
- State-based workflow transitions
- Automatic form numbering and state code generation
- CSV export functionality for transaction data

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
- State-based form locking and permissions
- Automatic form numbering with state codes
- File attachment handling for supporting documents
- Audit trail tracking for all changes
- Custom admin views for each user group
- Date-based filtering with custom date ranges
- Company-specific form filtering

### State Transitions
The system manages state transitions through the admin interface:
- Forms start in DRAFT state
- Can be moved through approval states
- Previous states are locked for editing
- Required data must be present before state transition
- Notifications and logging for state changes

### Security Features
- Role-based access control
- Company-specific data isolation
- File upload restrictions
- Audit logging of all changes
- State-based permission enforcement
- Unique constraints on critical records
