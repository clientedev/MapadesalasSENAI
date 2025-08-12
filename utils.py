import os
import json
import tempfile
import qrcode
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image as PILImage
from models import Schedule
from app import app
from flask import url_for, request

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
        
        # Create schedule headers with course info if available
        if any(schedule.technical_course for schedule in schedules):
            schedule_data = [['Dia', 'Disciplina', 'Professor', 'Curso', 'Horário']]
            col_widths = [1.2*inch, 1.8*inch, 1.3*inch, 1.2*inch, 1.2*inch]
        else:
            schedule_data = [['Dia da Semana', 'Disciplina', 'Professor', 'Horário']]
            col_widths = [1.5*inch, 2.2*inch, 1.8*inch, 1.2*inch]
        
        for schedule in schedules:
            # Truncate long text to prevent overflow
            subject = schedule.subject_name[:25] + '...' if len(schedule.subject_name) > 25 else schedule.subject_name
            professor = schedule.professor_name[:20] + '...' if len(schedule.professor_name) > 20 else schedule.professor_name
            
            if any(schedule.technical_course for schedule in schedules):
                course = (schedule.technical_course[:15] + '...' if schedule.technical_course and len(schedule.technical_course) > 15 
                         else schedule.technical_course) if schedule.technical_course else '-'
                schedule_data.append([
                    schedule.day_name,
                    subject,
                    professor,
                    course,
                    f"{schedule.start_time.strftime('%H:%M')}-{schedule.end_time.strftime('%H:%M')}"
                ])
            else:
                schedule_data.append([
                    schedule.day_name,
                    subject,
                    professor,
                    f"{schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}"
                ])
        
        schedule_table = Table(schedule_data, colWidths=col_widths)
        schedule_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), True),
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

def generate_room_qr_code(room):
    """Generate a QR code for a room with its standalone information page"""
    # Create the URL for standalone room information
    room_url = url_for('room_standalone', room_id=room.id, _external=True)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(room_url)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
    os.close(temp_fd)
    
    # Save QR code image
    qr_img.save(temp_path)
    
    return temp_path
