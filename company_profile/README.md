# Company Profile Django Application

## Introduction
The Company Profile application is a comprehensive Django-based system designed to manage and track company-related information, licenses, and various application workflows. It provides a structured approach to handling company data, production details, and application processes.

## Features
- Company profile management with detailed information
- License tracking and management system
- Workflow management for various application types
- Role-based access control for different user groups
- Comprehensive admin interface for managing records
- Audit logging with creation and update tracking
- File attachment handling for supporting documents
- State-based workflow transitions

## Usage
To use the Company Profile application:

1. Ensure all migrations are applied:
```bash
python manage.py migrate
```

2. Create user groups and assign permissions using the admin interface.

3. Access the admin interface at `/admin/company_profile/` to manage records.

4. Use the following main user groups to control access:
   - pro_company_application_accept
   - pro_company_application_approve
   - company_type_entaj
   - company_type_mokhalfat
   - company_type_emtiaz
   - company_type_sageer

## User Workflows
The application implements the following workflows through the admin interface:

### Company Management Workflow
1. Create new company profiles with detailed information
2. Manage company licenses and production details
3. Track factory information and capacities
4. Handle user roles and permissions

### Application Workflow
1. Submit various application types (e.g., foreigner movement, work plans, technical reports)
2. Process applications through state transitions:
   - SUBMITTED
   - ACCEPTED
   - APPROVED
   - REJECTED
3. Handle application-specific details and attachments
4. Manage notifications and email alerts

### Key Admin Features
- State-based application locking and permissions
- Automatic company details creation from related forms
- File attachment handling for supporting documents
- Audit trail tracking for all changes
- Custom admin views for each user group
- CSV export functionality for license data
- Company type-based filtering

### State Transitions
The system manages state transitions through the admin interface:
- Applications start in SUBMITTED state
- Can be moved to ACCEPTED state
- Can be approved to APPROVED state
- Can be rejected to REJECTED state
- Previous states are locked for editing
- Required data must be present before state transition
- Automatic email notifications for state changes

### Security Features
- Role-based access control
- Company type-based data isolation
- File upload restrictions
- Audit logging of all changes
- State-based permission enforcement
- Unique constraints on company codes and licenses
