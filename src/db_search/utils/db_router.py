class DBRouter:
    def db_for_read(self, model, **hints):
        """
        Attempts to read app from correct db.
        """
        # Only the bilbyui app needs to modify the migrations table (See bilbyui/migrations/0001_initial.py)
        if model._meta.app_label == 'migrations':
            return 'bilbyui'

        return model._meta.app_label

    def db_for_write(self, model, **hints):
        """
        Attempts to write the correct model to the correct db.
        """
        return model._meta.app_label

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow all relations
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Any django auth or contenttypes apps should be migrated
        if app_label in ['auth', 'contenttypes']:
            return True

        # Only allow migrations for apps belonging to the correct database
        return db == app_label
