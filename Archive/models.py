from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Database configuration
from config import settings
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    
    # Relationship to evaluations
    evaluations = relationship("Evaluation", back_populates="user")

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    feedback = Column(Text, nullable=False)  # JSON string of feedback
    strengths = Column(Text, nullable=False)  # JSON string of strengths
    areas_for_improvement = Column(Text, nullable=False)  # JSON string of areas
    detailed_errors = Column(Text, nullable=True)  # JSON string of detailed errors
    consolidated_scores = Column(Text, nullable=True)  # JSON string of consolidated scores
    cross_task_analysis = Column(Text, nullable=True)  # JSON string of cross-task analysis
    final_tef_writing_score = Column(Integer, nullable=True)  # Final TEF writing score (0-450)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="evaluations")

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create default testing user
def create_default_user():
    db = SessionLocal()
    try:
        # Check if testing user already exists
        existing_user = db.query(User).filter(User.username == "testing").first()
        if not existing_user:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            testing_user = User(
                username="testing",
                email="testing@example.com",
                hashed_password=pwd_context.hash("testing"),
                is_active=1
            )
            db.add(testing_user)
            db.commit()
            print("✅ Default testing user created successfully")
        else:
            print("ℹ️  Testing user already exists")
    except Exception as e:
        print(f"❌ Error creating testing user: {e}")
        db.rollback()
    finally:
        db.close()

# Initialize default user when module is imported
if __name__ == "__main__":
    create_default_user()
else:
    create_default_user()
