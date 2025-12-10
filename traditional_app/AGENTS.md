# Django Admin Portal Application Blueprint┃

## Project Overview

Create a modern, bilingual (Arabic RTL + English) Django web application that clone the Django admin interface with a custom frontend portal for employee self-service and management workflows.

## Technical Stack

### Backend

- Framework: Django (latest stable version)
- Authentication: Django's built-in auth system with custom user groups
- API: use Django REST Framework  for api.

### Frontend

- UI Framework: DaisyUI (Tailwind CSS component library) with cupcake theme.
- Direction: RTL (Right-to-Left) support for Arabic
- If django field has choices you should use get choices referance in template and never use static values.

## Styling Guidelines

### DaisyUI Theme

- Use semantic color classes (primary, success, error, warning)
- Card components for content blocks
- Table with zebra striping
- Badge components for status
- Button variants (btn-primary, btn-success, btn-error)
- Form controls (input, select, checkbox, file-input)
- Loading states (loading-spinner)

### Tailwind Utilities

- Responsive grid (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
- Spacing (p-4, mb-4, gap-4)
- Flexbox (flex, justify-between, items-center)
- Shadows (shadow-xl, shadow-lg)
- Hover effects (hover:shadow-2xl, transition-shadow)

### RTL Support

- dir="rtl" on html tag
- lang="ar" for Arabic
- Right-aligned text
- Reversed flex directions

### Custom Styles

/* Z-index fix for dropdowns */
.navbar { position: relative; z-index: 50; }

/* Dropdown menu colors */
.navbar details ul {
background-color: white;
color: gray;
}

/* Hover effects */
.navbar details ul li a:hover {
background-color: hsl(var(--p));
color: black;
}

### Accessibility Features

- High contrast text on backgrounds
- Clear visual states (hover, active, disabled)
- Semantic HTML structure
- Icon + text labels for better comprehension
- Proper form labels and ARIA attributes (via DaisyUI)

## Security Considerations

- Authentication: Use Django's login_required decorator
- Authorization: Check user groups in every view
- CSRF Protection: Include CSRF tokens in POST requests
- File Upload: Validate file types and sizes
- SQL Injection: Use Django ORM (no raw queries)
- XSS Prevention: React's built-in escaping
- Permission Checks: Both frontend (UI) and backend (API)

## Best Practices

- Separation of Concerns: Admin for management, Portal for self-service
- DRY Principle: Use mixins and base classes
- Consistent Naming: Follow Django conventions
- Verbose Names: Use gettext_lazy for i18n
- Error Handling: Try-except blocks with meaningful messages
- Logging: Track all state changes
- Documentation: Docstrings for models and complex functions
- Code Organization: Separate utilities into utils.py

## Customization Points

To adapt this blueprint for your use case:

- Replace Entity Types: Change Family/Moahil/BankAccount to your entities
- Adjust Workflow States: Modify state choices as needed
- Change User Groups: Define your own permission groups
- Customize Notifications: Replace Telegram with email/SMS/etc.
- Modify UI Theme: Change DaisyUI theme or use different component library
- Add Business Logic: Implement your specific validation rules
- Extend Data Model: Add fields specific to your domain
