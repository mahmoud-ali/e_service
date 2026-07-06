class DeductionsRouter:
    """
    Routes all reads/writes for the DeductionsView model to the 'deductions' database.
    All other models stay on 'default'.
    """

    router_app_labels = {"api_v1"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.router_app_labels and model.__name__ == "DeductionsView":
            return "deductions"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.router_app_labels and model.__name__ == "DeductionsView":
            return "deductions"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Prevent Django from trying to create this table — it's a view
        if db == "deductions":
            return False
        return None
