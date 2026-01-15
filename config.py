# class Config:
#     SQLALCHEMY_DATABASE_URI = "postgresql://postgres:root@localhost:5432/attendance"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SECRET_KEY = "attendance-secret-key"

class Config:
    
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:root@localhost:5432/attend"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key-change-this-in-production'