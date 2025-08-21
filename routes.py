import io
import json
import uuid
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, send_file, abort
from werkzeug.utils import secure_filename
from app import app, db
from models import Room, RoomImage, Schedule
from forms import RoomForm, ScheduleForm, SearchForm, BulkScheduleForm
from utils import generate_room_pdf, generate_room_qr_code, allowed_file
from sqlalchemy import or_

@app.route('/')
def index():
    search_form = SearchForm()
    rooms = Room.query.all()
    
    # Handle search and filters
    if request.args.get('search') or request.args.get('capacity_min') or \
       request.args.get('has_computers') or request.args.get('professor'):
        
        query = Room.query
        
        # Text search
        search_term = request.args.get('search', '').strip()
        if search_term:
            query = query.filter(or_(
                Room.name.contains(search_term),
                Room.location.contains(search_term)
            ))
        
        # Capacity filter
        capacity_min = request.args.get('capacity_min')
        if capacity_min:
            try:
                query = query.filter(Room.capacity >= int(capacity_min))
            except ValueError:
                pass
        
        # Computer filter
        has_computers = request.args.get('has_computers')
        if has_computers in ['0', '1']:
            query = query.filter(Room.has_computers == bool(int(has_computers)))
        
        # Professor filter
        professor = request.args.get('professor', '').strip()
        if professor:
            room_ids = db.session.query(Schedule.room_id).filter(
                Schedule.professor_name.contains(professor)
            ).distinct().all()
            if room_ids:
                query = query.filter(Room.id.in_([r[0] for r in room_ids]))
            else:
                query = query.filter(Room.id == -1)  # No results
        
        rooms = query.all()
    
    return render_template('index.html', rooms=rooms, search_form=search_form)

@app.route('/room/<int:room_id>')
def room_detail(room_id):
    room = Room.query.get_or_404(room_id)
    schedules = Schedule.query.filter_by(room_id=room_id).order_by(Schedule.day_of_week, Schedule.start_time).all()
    
    # Parse software list
    software_list = []
    if room.software_list:
        try:
            software_list = json.loads(room.software_list)
        except:
            software_list = room.software_list.split('\n') if room.software_list else []
    
    return render_template('room_detail.html', room=room, schedules=schedules, software_list=software_list)

@app.route('/room/new', methods=['GET', 'POST'])
def room_new():
    form = RoomForm()
    
    if form.validate_on_submit():
        room = Room(
            name=form.name.data,
            location=form.location.data,
            capacity=form.capacity.data,
            has_computers=form.has_computers.data,
            computer_passwords=form.computer_passwords.data,
            technical_course=form.technical_course.data
        )
        
        # Process software list
        if form.software_list.data:
            software_list = [s.strip() for s in form.software_list.data.split('\n') if s.strip()]
            room.software_list = json.dumps(software_list)
        
        db.session.add(room)
        db.session.flush()  # pega o room.id antes do commit
        
        # Handle image uploads
        if form.images.data:
            for file in form.images.data:
                if file and file.filename and allowed_file(file.filename):
                    room_image = RoomImage(
                        data=file.read(),  # salva os bytes no banco
                        original_filename=secure_filename(file.filename),
                        room_id=room.id
                    )
                    db.session.add(room_image)
        
        db.session.commit()
        flash('Sala criada com sucesso!', 'success')
        return redirect(url_for('room_detail', room_id=room.id))
    
    return render_template('room_form.html', form=form, title='Nova Sala')

@app.route('/room/<int:room_id>/edit', methods=['GET', 'POST'])
def room_edit(room_id):
    room = Room.query.get_or_404(room_id)
    form = RoomForm(room_id=room_id, obj=room)
    
    # Pre-populate software list
    if room.software_list:
        try:
            software_list = json.loads(room.software_list)
            form.software_list.data = '\n'.join(software_list)
        except:
            form.software_list.data = room.software_list
    
    if form.validate_on_submit():
        room.name = form.name.data
        room.location = form.location.data
        room.capacity = form.capacity.data
        room.has_computers = form.has_computers.data
        room.computer_passwords = form.computer_passwords.data
        room.technical_course = form.technical_course.data
        
        # Process software list
        if form.software_list.data:
            software_list = [s.strip() for s in form.software_list.data.split('\n') if s.strip()]
            room.software_list = json.dumps(software_list)
        else:
            room.software_list = None
        
        # Handle new image uploads
        if form.images.data:
            for file in form.images.data:
                if file and file.filename and allowed_file(file.filename):
                    room_image = RoomImage(
                        data=file.read(),
                        original_filename=secure_filename(file.filename),
                        room_id=room.id
                    )
                    db.session.add(room_image)
        
        db.session.commit()
        flash('Sala atualizada com sucesso!', 'success')
        return redirect(url_for('room_detail', room_id=room.id))
    
    return render_template('room_form.html', form=form, title='Editar Sala', room=room)

@app.route('/room/<int:room_id>/delete', methods=['POST'])
def room_delete(room_id):
    room = Room.query.get_or_404(room_id)
    
    db.session.delete(room)
    db.session.commit()
    flash('Sala excluída com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/room/<int:room_id>/image/<int:image_id>/delete', methods=['POST'])
def image_delete(room_id, image_id):
    room = Room.query.get_or_404(room_id)
    image = RoomImage.query.filter_by(id=image_id, room_id=room_id).first_or_404()
    
    db.session.delete(image)
    db.session.commit()
    flash('Imagem excluída com sucesso!', 'success')
    return redirect(url_for('room_detail', room_id=room_id))

@app.route('/room/image/<int:image_id>')
def get_room_image(image_id):
    image = RoomImage.query.get_or_404(image_id)
    return send_file(
        io.BytesIO(image.data),
        mimetype="image/jpeg",  # pode detectar pelo nome original
        as_attachment=False,
        download_name=image.original_filename
    )

@app.route('/schedule/new')
def schedule_new():
    form = ScheduleForm()
    return render_template('schedule_form.html', form=form, title='Novo Horário')

@app.route('/schedule/new', methods=['POST'])
def schedule_create():
    form = ScheduleForm()
    
    if form.validate_on_submit():
        schedule = Schedule(
            room_id=form.room_id.data,
            day_of_week=form.day_of_week.data,
            subject_name=form.subject_name.data,
            professor_name=form.professor_name.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            technical_course=form.technical_course.data,
            is_recurring=form.is_recurring.data
        )
        
        db.session.add(schedule)
        db.session.commit()
        flash('Horário criado com sucesso!', 'success')
        return redirect(url_for('room_detail', room_id=schedule.room_id))
    
    return render_template('schedule_form.html', form=form, title='Novo Horário')

@app.route('/schedule/<int:schedule_id>/edit', methods=['GET', 'POST'])
def schedule_edit(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    form = ScheduleForm(schedule_id=schedule_id, obj=schedule)
    
    if form.validate_on_submit():
        schedule.room_id = form.room_id.data
        schedule.day_of_week = form.day_of_week.data
        schedule.subject_name = form.subject_name.data
        schedule.professor_name = form.professor_name.data
        schedule.start_time = form.start_time.data
        schedule.end_time = form.end_time.data
        schedule.start_date = form.start_date.data
        schedule.end_date = form.end_date.data
        schedule.technical_course = form.technical_course.data
        schedule.is_recurring = form.is_recurring.data
        
        db.session.commit()
        flash('Horário atualizado com sucesso!', 'success')
        return redirect(url_for('room_detail', room_id=schedule.room_id))
    
    return render_template('schedule_form.html', form=form, title='Editar Horário', schedule=schedule)

@app.route('/schedule/<int:schedule_id>/delete', methods=['POST'])
def schedule_delete(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    room_id = schedule.room_id
    
    db.session.delete(schedule)
    db.session.commit()
    flash('Horário excluído com sucesso!', 'success')
    return redirect(url_for('room_detail', room_id=room_id))

@app.route('/room/<int:room_id>/pdf')
def room_pdf(room_id):
    room = Room.query.get_or_404(room_id)
    pdf_path = generate_room_pdf(room)
    
    return send_file(pdf_path, as_attachment=True, download_name=f'sala_{room.name}.pdf')

@app.route('/room/<int:room_id>/qrcode')
def room_qr_code(room_id):
    room = Room.query.get_or_404(room_id)
    qr_path = generate_room_qr_code(room)
    
    return send_file(qr_path, as_attachment=True, download_name=f'qrcode_sala_{room.name}.png', mimetype='image/png')

@app.route('/room/<int:room_id>/standalone')
def room_standalone(room_id):
    room = Room.query.get_or_404(room_id)
    schedules = Schedule.query.filter_by(room_id=room_id).order_by(Schedule.day_of_week, Schedule.start_time).all()
    
    # Parse software list
    software_list = []
    if room.software_list:
        try:
            software_list = json.loads(room.software_list)
        except:
            software_list = room.software_list.split('\n') if room.software_list else []
    
    return render_template('room_standalone.html', 
                         room=room, 
                         schedules=schedules, 
                         software_list=software_list,
                         now=datetime.now())

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

@app.route('/schedule/bulk', methods=['GET', 'POST'])
def schedule_bulk():
    form = BulkScheduleForm()
    
    if form.validate_on_submit():
        # Get selected days
        selected_days = []
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        for day_name, day_num in day_mapping.items():
            if getattr(form, day_name).data:
                selected_days.append(day_num)
        
        schedules_created = 0
        current_date = form.start_date.data
        end_date = form.end_date.data
        
        # Create schedules for each selected day within the date range
        while current_date <= end_date:
            if current_date.weekday() in selected_days:
                conflicting_schedule = Schedule.query.filter_by(
                    room_id=form.room_id.data,
                    day_of_week=current_date.weekday()
                ).filter(
                    Schedule.start_time < form.end_time.data,
                    Schedule.end_time > form.start_time.data
                ).first()
                
                if not conflicting_schedule:
                    schedule = Schedule(
                        room_id=form.room_id.data,
                        day_of_week=current_date.weekday(),
                        subject_name=form.technical_course.data,
                        professor_name=form.professor_name.data,
                        start_time=form.start_time.data,
                        end_time=form.end_time.data,
                        start_date=current_date,
                        end_date=current_date,
                        technical_course=form.technical_course.data,
                        is_recurring=False
                    )
                    db.session.add(schedule)
                    schedules_created += 1
            
            current_date += timedelta(days=1)
        
        if schedules_created > 0:
            db.session.commit()
            flash(f'{schedules_created} agendamentos criados com sucesso!', 'success')
            room = Room.query.get(form.room_id.data)
            return redirect(url_for('room_detail', room_id=room.id))
        else:
            flash('Nenhum agendamento foi criado. Verifique se há conflitos de horário.', 'warning')
    
    return render_template('bulk_schedule_form.html', form=form, title='Agendamento em Lote')

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500

