from backend.models import db
from sqlalchemy.dialects.postgresql import ARRAY



class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(500), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    organizer = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(500), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    tags = db.Column(ARRAY(db.String), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    source_link = db.Column(db.String(500), nullable=False)