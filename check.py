'''
from database.structure import SessionLocal
from models import model

db = SessionLocal()
admin = db.query(model.Users).filter(model.Users.email == "admin1@admin.itu.edu").first()
print(f"Email: {admin.email}, Role: {admin.role}, ID: {admin.id}")
db.close()
'''