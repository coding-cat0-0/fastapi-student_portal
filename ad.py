'''
from sqlalchemy.orm import Session
from database.structure import SessionLocal, engine
from models import model
from hasher.hashing import Hash

# Make sure tables are created
model.Base.metadata.create_all(bind=engine)

# Start a DB session
db: Session = SessionLocal()

# Admin details
admin_email = "admin1@admin.itu.edu"
admin_password = "Admin@01"

# Check if admin already exists
existing_admin = db.query(model.Users).filter(model.Users.email == admin_email).first()

if not existing_admin:
    admin = model.Users(
    name="Admin",
    email=admin_email,
    password=Hash.bcrypt(admin_password),
    role="admin"
)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("✅ Admin created successfully.")
else:
    print("⚠️ Admin already exists.")

# Close DB session
db.close()
'''