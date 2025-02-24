import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///langportal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False