from app import db
from datetime import datetime, time
from sqlalchemy import CheckConstraint

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    has_computers = db.Column(db.Boolean, default=False)
    software_list = db.Column(db.Text)  # JSON string of software list
    computer_passwords = db.Column(db.Text)  # Encrypted passwords
    technical_course = db.Column(db.String(200))  # Main technical course that runs in this room
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = db.relationship('RoomImage', backref='room', lazy=True, cascade='all, delete-orphan')
    schedules = db.relationship('Schedule', backref='room', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Room {self.name}>'


class RoomImage(db.Model):
    """
    Modelo antigo para imagens de sala (referência a arquivos).
    Se quiser migrar 100% para o banco, pode ser desativado futuramente.
    """
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RoomImage {self.filename}>'


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    subject_name = db.Column(db.String(100), nullable=False)
    professor_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    start_date = db.Column(db.Date)  # When this schedule period starts
    end_date = db.Column(db.Date)    # When this schedule period ends
    technical_course = db.Column(db.String(200))  # Technical course name
    is_recurring = db.Column(db.Boolean, default=True)  # If this is a recurring schedule
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add constraint to ensure end_time > start_time
    __table_args__ = (
        CheckConstraint('start_time < end_time', name='check_time_order'),
        CheckConstraint('day_of_week >= 0 AND day_of_week <= 6', name='check_day_of_week'),
    )
    
    def __repr__(self):
        return f'<Schedule {self.subject_name} - {self.professor_name}>'
    
    @property
    def day_name(self):
        days = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
                'Sexta-feira', 'Sábado', 'Domingo']
        return days[self.day_of_week]


class File(db.Model):
    """
    Modelo para armazenar qualquer arquivo (imagem ou planilha) diretamente no Postgres.
    """
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mimetype = db.Column(db.String(50), nullable=False)  # ex: image/png, application/vnd.ms-excel
    data = db.Column(db.LargeBinary, nullable=False)  # conteúdo binário do arquivo
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<File {self.filename}>'
