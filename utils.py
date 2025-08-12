import os
import json
import tempfile
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image as PILImage
from models import Schedule
from app import app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_room_pdf(room):
    """Generate a comprehensive PDF report for a room"""
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
    os.close(temp_fd)
    
    # Create PDF document
    doc = SimpleDocTemplate(temp_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph(f"Relatório da Sala: {room.name}", title_style))
    story.append(Spacer(1, 20))
    
    # Room information
    story.append(Paragraph("Informações Básicas", styles['Heading2']))
    
    room_info = [
        ['Campo', 'Valor'],
        ['Nome da Sala', room.name],
        ['Localização', room.location],
        ['Capacidade Máxima', str(room.capacity)],
        ['Possui Computadores', 'Sim' if room.has_computers else 'Não'],
        ['Data de Criação', room.created_at.strftime('%d/%m/%Y %H:%M')],
        ['Última Atualização', room.updated_at.strftime('%d/%m/%Y %H:%M')]
    ]
    
    room_table = Table(room_info, colWidths=[2*inch, 4*inch])
    room_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(room_table)
    story.append(Spacer(1, 20))
    
    # Software information
    if room.has_computers and room.software_list:
        story.append(Paragraph("Softwares Instalados", styles['Heading2']))
        try:
            software_list = json.loads(room.software_list)
            for i, software in enumerate(software_list, 1):
                story.append(Paragraph(f"{i}. {software}", styles['Normal']))
        except:
            # Fallback for plain text
            software_lines = room.software_list.split('\n')
            for i, software in enumerate(software_lines, 1):
                if software.strip():
                    story.append(Paragraph(f"{i}. {software.strip()}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Password information (if exists)
    if room.computer_passwords:
        story.append(Paragraph("Informações de Acesso", styles['Heading2']))
        story.append(Paragraph(f"Senhas dos Computadores: {room.computer_passwords}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Schedule information
    schedules = Schedule.query.filter_by(room_id=room.id).order_by(Schedule.day_of_week, Schedule.start_time).all()
    if schedules:
        story.append(Paragraph("Agenda de Uso", styles['Heading2']))
        
        schedule_data = [['Dia da Semana', 'Disciplina', 'Professor', 'Horário']]
        for schedule in schedules:
            schedule_data.append([
                schedule.day_name,
                schedule.subject_name,
                schedule.professor_name,
                f"{schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}"
            ])
        
        schedule_table = Table(schedule_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        schedule_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(schedule_table)
        story.append(Spacer(1, 20))
    
    # Images
    if room.images:
        story.append(Paragraph("Imagens da Sala", styles['Heading2']))
        
        for image in room.images:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            if os.path.exists(image_path):
                try:
                    # Open and resize image if necessary
                    pil_img = PILImage.open(image_path)
                    
                    # Calculate dimensions to fit within page
                    max_width = 4 * inch
                    max_height = 3 * inch
                    
                    img_width, img_height = pil_img.size
                    aspect_ratio = img_width / img_height
                    
                    if img_width > max_width:
                        img_width = max_width
                        img_height = img_width / aspect_ratio
                    
                    if img_height > max_height:
                        img_height = max_height
                        img_width = img_height * aspect_ratio
                    
                    # Add image to PDF
                    img = Image(image_path, width=img_width, height=img_height)
                    story.append(img)
                    story.append(Paragraph(f"Arquivo: {image.original_filename}", styles['Caption']))
                    story.append(Spacer(1, 15))
                    
                except Exception as e:
                    story.append(Paragraph(f"Erro ao carregar imagem: {image.original_filename}", styles['Normal']))
                    story.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(story)
    
    return temp_path
