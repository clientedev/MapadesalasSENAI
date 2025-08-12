# Overview

This is a classroom management system built for Escola SENAI "Morvan Figueiredo" with Flask that helps manage room information, schedules, and resources. The application allows users to create, view, edit, and delete classroom records along with their schedules. Key features include room search and filtering, image uploads for rooms, schedule management with bulk scheduling for long periods (e.g., Monday to Friday for several months), technical course tracking, and PDF report generation, and QR code sharing functionality.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Styling**: Dark theme using Replit's Bootstrap theme with custom CSS
- **JavaScript**: Vanilla JavaScript for form validation, tooltips, and image previews
- **Forms**: Flask-WTF with WTForms for server-side validation and CSRF protection

## Backend Architecture
- **Framework**: Flask web framework with modular structure
- **Database ORM**: SQLAlchemy with declarative base model approach
- **File Handling**: Werkzeug for secure file uploads with validation
- **PDF Generation**: ReportLab for creating comprehensive room reports
- **QR Code Generation**: QRCode library for creating shareable room links
- **Image Processing**: PIL (Pillow) for image handling and optimization

## Data Model Design
- **Room Entity**: Core entity storing room details, capacity, computer availability, software lists, and technical course information
- **RoomImage Entity**: Separate table for multiple image uploads per room
- **Schedule Entity**: Enhanced time-based scheduling with day-of-week, time constraints, date ranges, technical course tracking, and recurring schedule options
- **Relationships**: One-to-many relationships between rooms and both images and schedules

## Recent Updates (August 2025)
- Added technical course field to Room model for tracking main courses that use each room
- Enhanced Schedule model with date ranges (start_date, end_date), technical course tracking, and recurring schedule flags
- Implemented bulk scheduling functionality for creating long-period schedules (e.g., Monday-Friday for several months)
- Updated branding to "Escola SENAI Morvan Figueiredo" throughout the application
- Added new BulkScheduleForm with multi-day selection and date range capabilities
- Enhanced UI to display technical course information in room details and schedule tables
- Created dedicated bulk scheduling template with quick day selection buttons
- Implemented QR code generation system that provides mobile-optimized room information when scanned
- Added mobile-responsive QR view template for enhanced mobile user experience
- Integrated QRCode library for generating downloadable QR codes linked to room details

## File Storage Strategy
- **Upload Directory**: Local file system storage in `uploads/` folder
- **File Validation**: Restricted to image formats (PNG, JPG, JPEG, GIF)
- **Security**: Secure filename generation to prevent directory traversal attacks
- **Size Limits**: 16MB maximum file upload size

## Database Design
- **Primary Database**: SQLite for development with PostgreSQL support via environment variables
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability
- **Constraints**: Database-level constraints for time validation and day-of-week ranges
- **Timestamps**: Automatic creation and update timestamps on entities

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web framework for request handling and routing
- **SQLAlchemy**: Database ORM for data persistence
- **Flask-SQLAlchemy**: Flask integration for SQLAlchemy
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering

## UI and Frontend Libraries
- **Bootstrap 5**: CSS framework via Replit's dark theme CDN
- **Font Awesome**: Icon library for UI elements
- **Custom CSS**: Additional styling for enhanced user experience

## File Processing Libraries
- **Werkzeug**: File upload utilities and security
- **Pillow (PIL)**: Image processing and validation
- **ReportLab**: PDF generation for room reports

## Development and Production Support
- **ProxyFix**: Werkzeug middleware for handling proxy headers
- **Python Logging**: Built-in logging configuration for debugging

## Database Support
- **SQLite**: Default development database (included in Python)
- **PostgreSQL**: Production database support via psycopg2 (configurable via DATABASE_URL)