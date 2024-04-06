from bootstrap3.renderers import FormRenderer as Bootsrtap3FormRenderer
from bootstrap3.forms import (
    render_field,
)

class FormRenderer(Bootsrtap3FormRenderer):
    def render_fields(self):
        template = ""
        layout = [] 
        if not hasattr(self.form,'layout'):
            return super().render_fields()

        layout = self.form.layout 

        for row in layout:
            template += '<div class="row">'
            if type(row) is str:
                row = [row]

            for field_name in row:
                template += '<div class="col-md-'+str(12//len(row))+'">'
                if field_name:
                    field = self.form.fields.get(field_name).get_bound_field(self.form,field_name)
                    template += render_field(
                            field,
                            layout=self.layout,
                            form_group_class=self.form_group_class,
                            field_class=self.field_class,
                            label_class=self.label_class,
                            show_label=self.show_label,
                            show_help=self.show_help,
                            exclude=self.exclude,
                            set_placeholder=self.set_placeholder,
                            size=self.size,
                            horizontal_label_class=self.horizontal_label_class,
                            horizontal_field_class=self.horizontal_field_class,
                            error_css_class=self.error_css_class,
                            required_css_class=self.required_css_class,
                            bound_css_class=self.bound_css_class,
                        )
                else:
                    template += '&nbsp;'
                template += '</div>'
            template += '</div>'
        return template