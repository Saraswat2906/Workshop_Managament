import os
# Setting up the postgressql connection string here
#Format: "postgresql://USERNAME:PASSWORD@localhost/DATABASE_NAME"
# Database_url="postgresql://postgres:Ada@6402628@localhost/Workshop Management"
Database_url = "postgresql://postgres:Ada%406402628@localhost/Workshop Management"

class config:
    SQLALCHEMY_DATABASE_URI = Database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False