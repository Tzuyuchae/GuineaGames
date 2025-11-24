from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    pets = relationship("Pet", back_populates="owner")

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    species = Column(String)
    color = Column(String)
    age_months = Column(Integer, default=0)
    health = Column(Integer, default=100)
    speed = Column(Integer, default=4)
    hunger = Column(Integer, default=100)
    endurance = Column(Integer, default=4)
    score = Column(Integer, default = 0)
    sizeScalar = Column(Float, default = 0.5)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="pets")

    #called for each pig when read in from DB
    def newPet(self, gp_id, o_id, name, species, color, age_month, hp, spd, hunger, endurance, score, sizeScalar):
        __tablename_ = "pets"
        self.id = gp_id
        self.owner_id = o_id
        self.name = name
        self.species = species
        self.color = color
        self.age_months = age_month
        self.health = hp
        self.speed = spd
        self.hunger = hunger
        self.endurance = endurance
        self.score = score
        self.sizeScalar = sizeScalar
        self.last_updated = datetime.datetime
    
    def get_closing_update_info(self):
        gpInfo = [self.id, self.name, self.age_months, self.health, self.speed, self.hunger, self.endurance, self.score, self.sizeScalar, datetime.datetime,]
        return gpInfo

    def get_name(self):
        return self.name
    def set_name(self, arg):
        self.name = arg

    def get_hunger(self):
        return self.hunger
    def set_hunger(self, arg):
        self.hunger = arg
    def decr_hunger(self):
        self.hunger = max(0, self.hunger - 1)
    
    def get_age_Months(self):
        return self.age_months
    def add_to_age_months(self, arg):
        self.age_months = self.add_to_age_months() + arg
    def inc_age_months(self):
        self.age_months += 1
    
    def get_speed(self):
        return self.speed
    def add_to_speed(self, arg):
        self.speed = self.get_speed() + arg
    def speed_decrease_old_pigs(self):
        self.speed = max(0, self.get_speed() - 2)

    def get_endurance(self):
        return self.endurance
    def add_to_endurance(self, arg):
        self.endurance = self.get_endurance() + arg
    def endurance_decrease_old_age(self):
        self.endurance = max(0, self.get_endurance() - 2)

    def get_size(self):
        return self.sizeScalar
    def set_size(self, arg):
        self.sizeScalar = arg
    def set_size_full_grown(self):
        self.sizeScalar = 1

    def get_score(self):
        return self.score
    def add_to_score(self, arg):
        self.score = self.get_score(arg)
    
    def get_last_updated(self):
        return self.last_updated
    def refresh_last_updated(self):
        self.last_updated = datetime.datetime