from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, DateTime, Table, Column
from database import metadata

template = Table(
    "templates",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(100)),
    Column("preview_image", String(255)),
    Column("document_path", String(255)),
    Column("form_type", String(50)),
    Column("last_modified", DateTime, default=datetime.utcnow),
    Column("author_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    # Column("date", DateTime, default=datetime.utcnow)
)

letter_history = Table(
    "letter_history",
    metadata,
    Column("id", Integer, primary_key=True), #
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")), #
    Column("template_id", Integer, ForeignKey("templates.id")), #
    Column("file_path", String(255)),
    Column("date", DateTime, default=datetime.utcnow) #
)

adressee = Table(
    "adressee",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("full_name", String(100)),
    Column("organization", String(100)),
    Column("position", String(100))
)

user = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_number", String(50), unique=True),
    Column("full_name", String(100)),
    Column("email", String(100), unique=True),
    Column("phone_number", String(20)),
    Column("password", String(255))
)

signer = Table(
    "signers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("position", String(100)),
    Column("full_name", String(100)),
    Column("faximili_id", Integer, ForeignKey("faximili.id"))
)

faximili = Table(
    "faximili",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("file_path", String(255))
)

employee = Table(
    "employees",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("full_name", String(100)),
    Column("position", String(100)),
    Column("notebook_id", Integer, ForeignKey("nootebooks.id"))
)

notebook = Table(
    "nootebooks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("notebooks_name", String(100)),
    Column("serial_number", String(50)),
    Column("mac_address", String(50))
)

organization = Table(
    "organization",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("location_name", String(100)),
    Column("areas_id", Integer, ForeignKey("areas.id"))
)

area = Table(
    "areas",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("areas_name", String(100))
)