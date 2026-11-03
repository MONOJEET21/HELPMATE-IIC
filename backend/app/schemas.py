from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = "customer"
    phone: str | None = None
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    phone: str | None
    model_config = ConfigDict(from_attributes=True)
class LoginInput(BaseModel):
    email: EmailStr
    password: str
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
class JobCreate(BaseModel):
    title: str
    category: str
    description: str
    location: str
    salary: str | None = None
class JobOut(BaseModel):
    id: int
    title: str
    category: str
    description: str
    location: str
    salary: str | None
    owner_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class ApplicationCreate(BaseModel):
    message: str | None = None
class FarmCreate(BaseModel):
    name: str
    crop: str | None = None
    area_acres: float | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
class FarmOut(BaseModel):
    id: int
    name: str
    crop: str | None
    area_acres: float | None
    latitude: float | None
    longitude: float | None
    owner_id: int
    model_config = ConfigDict(from_attributes=True)
class SensorInput(BaseModel):
    device_id: str
    farm_id: int | None = None
    soil_moisture: float | None = None
    temperature: float | None = None
    ph: float | None = None
    nitrogen: float | None = None
    phosphorus: float | None = None
    potassium: float | None = None
class SensorOut(BaseModel):
    id: int
    device_id: str
    farm_id: int | None
    soil_moisture: float | None
    temperature: float | None
    ph: float | None
    nitrogen: float | None
    phosphorus: float | None
    potassium: float | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class ListingCreate(BaseModel):
    title: str
    description: str
    category: str
    price: float = Field(ge=0)
    unit: str = "item"
    location: str
class ListingOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    unit: str
    location: str
    seller_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DeviceCommandCreate(BaseModel):
    device_id: str
    command: str = Field(min_length=2, max_length=80)
    payload: dict = {}

class DeviceCommandOut(BaseModel):
    id: int
    device_id: str
    command: str
    payload: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WorkerProfileUpdate(BaseModel):
    skills: str = ""
    experience_years: int = Field(default=0, ge=0, le=60)
    preferred_location: str = ""
    expected_salary: str = ""
    bio: str = ""
