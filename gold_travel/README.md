# Gold Travel Django Application

## Introduction
The Gold Travel application is a Django-based system designed to manage and track the movement of gold and silver between states and for export purposes. It provides a structured approach to handling gold movement forms, certificates, and related documentation.

## Features
- State-based gold movement tracking
- Export and re-export form management
- Silver export management
- Role-based access control for state representatives
- Comprehensive admin interface for managing records
- Audit logging with creation and update tracking
- File attachment handling for supporting documents
- State-based workflow transitions
- Automatic form numbering and state code generation
- CSV export functionality for transaction data

## Usage
To use the Gold Travel application:

1. Ensure all migrations are applied:
```bash
python manage.py migrate
```

2. Create state representatives using the admin interface at `/admin/gold_travel/`

3. Use the following main user groups to control access:
   - gold_travel_manager
   - gold_travel_state
   - gold_travel_ssmo

4. Import historical data using the `import_history` management command:
```bash
python manage.py import_history
```

## User Workflows
The application implements the following workflows through the admin interface:

### Gold Movement Workflow
1. Create new gold movement forms with:
   - Owner details
   - Representative information
   - Gold weight and alloy details
   - Supporting documents
2. Process forms through state transitions:
   - DRAFT
   - SMRC
   - MINISTRY OF MINERALS
   - MINING POLICE
   - MILITARY INTELLIGENCE
   - SSMO
   - CANCELED
3. Generate movement certificates
4. Export data to CSV for reporting

### Key Admin Features
- State-based form locking and permissions
- Automatic form numbering with state codes
- File attachment handling for supporting documents
- Audit trail tracking for all changes
- Custom admin views for each user group
- Date-based filtering with custom date ranges
- State-specific form filtering

### State Transitions
The system manages state transitions through the admin interface:
- Forms start in DRAFT state
- Can be moved through approval states
- Can be canceled to CANCELED state
- Previous states are locked for editing
- Required data must be present before state transition
- Notifications and logging for state changes

### Security Features
- Role-based access control
- State-specific data isolation
- File upload restrictions
- Audit logging of all changes
- State-based permission enforcement
- Unique constraints on state representatives
