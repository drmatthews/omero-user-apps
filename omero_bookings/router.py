class OmeroBookingsRouter(object):
    """
    A router to control all database operations on models in the
    omero_signup application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read omero_signup models go to omero_signup_db.
        """
        if model._meta.app_label == 'omero_bookings':
            return 'omero_bookings_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write omero_signup models go to omero_bookings_db.
        """
        if model._meta.app_label == 'omero_bookings':
            return 'omero_bookings_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the omero_signup app is involved.
        """
        if obj1._meta.app_label == 'omero_bookings' or \
           obj2._meta.app_label == 'omero_bookings':
           return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the omero_signup app only appears in the 'omero_bookings_db'
        database.
        """
        if app_label == 'omero_bookings':
            return db == 'omero_bookings_db'
        return None