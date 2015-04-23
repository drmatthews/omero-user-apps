import json
CUSTOM_SETTINGS_MAPPINGS = {
    "omero.web.omero_signup.databases": ["DATABASES",\
    '{"omero_signup_db": {\
        "ENGINE": "django.db.backends.postgresql_psycopg2",\
        "NAME": "omero_signup_db",\
        "USER": "omero_signup_db_user",\
        "PASSWORD": "pkclpha",\
        "HOST": "localhost"\
        }\
    }', json.loads, "database global"],

    "omero.web.omero_signup.database_routers" : ["DATABASE_ROUTERS",\
    '["omero_signup.router.OmerosignupRouter"]', json.loads, "database routers"]
}