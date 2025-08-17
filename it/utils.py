def field_has_choices(field):
    # Check if the field has a 'choices' attribute
    if not hasattr(field, 'choices'):
        return False
    
    # Get the value of `choices`
    choices = field.choices
    
    # Handle callable choices (dynamic)
    if callable(choices):
        try:
            choices = choices()  # Execute the callable
        except:
            return False

   # Check if choices is None or not iterable
    if choices is None:
        return False

    # Ensure choices is iterable (e.g., list, tuple)
    try:
        iter(choices)  # Check if iterable
    except TypeError:
        return False

    # Check if choices are non-empty
    return bool(list(choices))  # Convert to list to handle generators

def display_field(instance, field):
    if field_has_choices(field):
        return str(getattr(instance, "get_"+field.name+"_display")())
    else:
        return str(getattr(instance, field.name))

def queryset_to_markdown(qs,exclude=[],newline="<br/>"):
    if qs.count() > 0:
        instance = qs.first()
        headers = "| " + " | ".join([str(field.verbose_name) for field in instance._meta.fields if field.name not in exclude]) + " |"
        separator = "| " + " | ".join(["-" * len(str(field.verbose_name)) for field in instance._meta.fields if field.name not in exclude]) + " |"

        values = ""
        for instance in qs:
            values += "| " + " | ".join([display_field(instance, field) for field in instance._meta.fields if field.name not in exclude]) + " |" + newline
        
        markdown = f"{headers}{newline}{separator}{newline}{values}"
        return markdown

