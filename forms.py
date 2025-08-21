from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, IntegerField, BooleanField, TextAreaField, SelectField, TimeField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError, Optional
from wtforms.widgets import PasswordInput
from models import Room, Schedule, Patrimonio
from datetime import time, date


class RoomForm(FlaskForm):
    name = StringField('Nome da Sala', validators=[DataRequired(), Length(min=1, max=100)])
    location = StringField('Localização', validators=[DataRequired(), Length(min=1, max=200)])
    capacity = IntegerField('Capacidade Máxima', validators=[DataRequired(), NumberRange(min=1, max=1000)])
    has_computers = BooleanField('Possui Computadores')
    software_list = TextAreaField('Softwares Instalados (um por linha)')
    computer_passwords = StringField('Senhas dos Computadores', widget=PasswordInput(hide_value=False))
    technical_course = StringField('Curso Técnico Principal', validators=[Length(max=200)])
    images = MultipleFileField('Imagens da Sala', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Apenas imagens são permitidas!')
    ])
    submit = SubmitField('Salvar Sala')
    
    def __init__(self, room_id=None, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)
        self.room_id = room_id
    
    def validate_name(self, field):
        room = Room.query.filter_by(name=field.data).first()
        if room and (not self.room_id or room.id != self.room_id):
            raise ValidationError('Uma sala com este nome já existe.')


class PatrimonioForm(FlaskForm):
    name = StringField('Nome do Patrimônio', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Descrição', validators=[Optional()])
    file = FileField('Planilha do Patrimônio', validators=[
        FileAllowed(['xls', 'xlsx', 'csv'], 'Apenas planilhas são permitidas!')
    ])
    submit = SubmitField('Salvar Patrimônio')
    
    def __init__(self, patrimonio_id=None, *args, **kwargs):
        super(PatrimonioForm, self).__init__(*args, **kwargs)
        self.patrimonio_id = patrimonio_id
    
    def validate_name(self, field):
        patrimonio = Patrimonio.query.filter_by(name=field.data).first()
        if patrimonio and (not self.patrimonio_id or patrimonio.id != self.patrimonio_id):
            raise ValidationError('Já existe um patrimônio com este nome.')


class ScheduleForm(FlaskForm):
    room_id = SelectField('Sala', coerce=int, validators=[DataRequired()])
    day_of_week = SelectField('Dia da Semana', choices=[
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo')
    ], coerce=int, validators=[DataRequired()])
    subject_name = StringField('Nome da Disciplina', validators=[DataRequired(), Length(min=1, max=100)])
    professor_name = StringField('Nome do Professor', validators=[DataRequired(), Length(min=1, max=100)])
    technical_course = StringField('Curso Técnico', validators=[Length(max=200)])
    start_time = TimeField('Horário de Início', validators=[DataRequired()])
    end_time = TimeField('Horário de Término', validators=[DataRequired()])
    start_date = DateField('Data de Início do Período', validators=[Optional()])
    end_date = DateField('Data de Fim do Período', validators=[Optional()])
    is_recurring = BooleanField('Horário Recorrente', default=True)
    submit = SubmitField('Salvar Horário')
    
    def __init__(self, schedule_id=None, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.schedule_id = schedule_id
        self.room_id.choices = [(room.id, room.name) for room in Room.query.order_by(Room.name).all()]
    
    def validate_end_time(self, field):
        if self.start_time.data and field.data <= self.start_time.data:
            raise ValidationError('O horário de término deve ser posterior ao horário de início.')
    
    def validate_end_date(self, field):
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError('A data de fim deve ser posterior à data de início.')
    
    def validate_room_id(self, field):
        if self.start_time.data and self.end_time.data and self.day_of_week.data is not None:
            query = Schedule.query.filter_by(
                room_id=field.data,
                day_of_week=self.day_of_week.data
            ).filter(
                Schedule.start_time < self.end_time.data,
                Schedule.end_time > self.start_time.data
            )
            if self.schedule_id:
                query = query.filter(Schedule.id != self.schedule_id)
            if query.first():
                raise ValidationError('Existe um conflito de horário com outro agendamento nesta sala.')


class SearchForm(FlaskForm):
    search = StringField('Buscar')
    capacity_min = IntegerField('Capacidade Mínima')
    has_computers = SelectField('Possui Computadores', choices=[
        ('', 'Todos'),
        ('1', 'Sim'),
        ('0', 'Não')
    ])
    professor = StringField('Professor')
    submit = SubmitField('Buscar')


class BulkScheduleForm(FlaskForm):
    room_id = SelectField('Sala', coerce=int, validators=[DataRequired()])
    technical_course = StringField('Curso Técnico', validators=[DataRequired(), Length(min=1, max=200)])
    professor_name = StringField('Nome do Professor', validators=[DataRequired(), Length(min=1, max=100)])
    
    monday = BooleanField('Segunda-feira')
    tuesday = BooleanField('Terça-feira')
    wednesday = BooleanField('Quarta-feira')
    thursday = BooleanField('Quinta-feira')
    friday = BooleanField('Sexta-feira')
    saturday = BooleanField('Sábado')
    sunday = BooleanField('Domingo')
    
    start_time = TimeField('Horário de Início', validators=[DataRequired()])
    end_time = TimeField('Horário de Término', validators=[DataRequired()])
    start_date = DateField('Data de Início do Período', validators=[DataRequired()])
    end_date = DateField('Data de Fim do Período', validators=[DataRequired()])
    
    submit = SubmitField('Criar Agendamentos')
    
    def __init__(self, *args, **kwargs):
        super(BulkScheduleForm, self).__init__(*args, **kwargs)
        self.room_id.choices = [(room.id, room.name) for room in Room.query.order_by(Room.name).all()]
    
    def validate_end_time(self, field):
        if self.start_time.data and field.data <= self.start_time.data:
            raise ValidationError('O horário de término deve ser posterior ao horário de início.')
    
    def validate_end_date(self, field):
        if self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('A data de fim deve ser posterior à data de início.')
    
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        days_selected = any([
            self.monday.data, self.tuesday.data, self.wednesday.data,
            self.thursday.data, self.friday.data, self.saturday.data, self.sunday.data
        ])
        if not days_selected:
            self.monday.errors.append('Selecione pelo menos um dia da semana.')
            return False
        return True

