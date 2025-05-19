from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TemplateCreate(BaseModel):
    title: str
    preview_image: str
    document_path: str
    last_modified: datetime
    author_id: int
    form_type: str


class TemplateUpdate(BaseModel):
    title: Optional[str] = None
    preview_image: Optional[str] = None
    document_path: Optional[str] = None
    last_modified: Optional[datetime] = None
    author_id: Optional[int] = None


class TemplateRead(BaseModel):
    id: int
    title: str
    preview_image: str
    document_path: str
    last_modified: datetime
    form_type: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    user_number: str
    full_name: str
    email: str
    phone_number: Optional[str] = None
    password: str

class UserUpdate(BaseModel):
    user_number: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None

class UserRead(BaseModel):
    id: int
    user_number: str
    full_name: str
    email: str
    phone_number: Optional[str]

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    login: str
    password: str


class AdresseeCreate(BaseModel):
    full_name: str
    organization: Optional[str] = None
    position: Optional[str] = None


class AdresseeUpdate(BaseModel):
    full_name: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None


class AdresseeRead(BaseModel):
    id: int
    full_name: str
    organization: Optional[str]
    position: Optional[str]

    class Config:
        from_attributes = True


# === Signer ===
class SignerCreate(BaseModel):
    position: str
    full_name: str
    faximili_id: int


class SignerUpdate(BaseModel):
    position: Optional[str] = None
    full_name: Optional[str] = None
    faximili_id: Optional[int] = None


class SignerRead(BaseModel):
    id: int
    position: str
    full_name: str
    faximili_id: int

    class Config:
        from_attributes = True


# === Faximili ===
class FaximiliCreate(BaseModel):
    file_path: str


class FaximiliUpdate(BaseModel):
    file_path: Optional[str] = None


class FaximiliRead(BaseModel):
    id: int
    file_path: str

    class Config:
        from_attributes = True


# === LetterHistory ===
class LetterHistoryCreate(BaseModel):
    user_id: int
    signer_id: int
    template_id: int
    file_path: str
    adressee_id: int


class LetterHistoryUpdate(BaseModel):
    user_id: Optional[int] = None
    signer_id: Optional[int] = None
    template_id: Optional[int] = None
    file_path: Optional[str] = None
    adressee_id: Optional[int] = None


class LetterHistoryRead(BaseModel):
    id: int
    user_id: int
    signer_id: int
    template_id: int
    file_path: str
    date: datetime
    adressee_id: int

    class Config:
        from_attributes = True


# === Notebook ===
class NotebookCreate(BaseModel):
    notebooks_name: str
    serial_number: str
    mac_address: str


class NotebookUpdate(BaseModel):
    notebooks_name: Optional[str] = None
    serial_number: Optional[str] = None
    mac_address: Optional[str] = None


class NotebookRead(BaseModel):
    id: int
    notebooks_name: str
    serial_number: str
    mac_address: str

    class Config:
        from_attributes = True


# === Organization ===
class OrganizationCreate(BaseModel):
    location_name: str
    areas_id: int


class OrganizationUpdate(BaseModel):
    location_name: Optional[str] = None
    areas_id: Optional[int] = None


class OrganizationRead(BaseModel):
    id: int
    location_name: str
    areas_id: int

    class Config:
        from_attributes = True


# === Area ===
class AreaCreate(BaseModel):
    areas_name: str


class AreaUpdate(BaseModel):
    areas_name: Optional[str] = None


class AreaRead(BaseModel):
    id: int
    areas_name: str

    class Config:
        from_attributes = True


# === Employee ===
class EmployeeCreate(BaseModel):
    full_name: str
    position: str
    notebook_id: int
    organization_id: int


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    notebook_id: Optional[int] = None
    organization_id: Optional[int] = None


class EmployeeRead(BaseModel):
    id: int
    full_name: str
    position: str
    notebook_id: int
    organization_id: int

    class Config:
        from_attributes = True