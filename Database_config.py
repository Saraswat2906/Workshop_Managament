import os
# Setting up the postgressql connection string here
#Format: "postgresql://USERNAME:PASSWORD@localhost/DATABASE_NAME"



class config:
    SQLALCHEMY_DATABASE_URI = Database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
