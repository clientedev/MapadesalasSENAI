// Main JavaScript for Mapa de Salas application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // File input preview for images
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(event) {
            const files = event.target.files;
            const previewContainer = document.getElementById('imagePreview');
            
            if (previewContainer) {
                previewContainer.innerHTML = '';
                
                for (let i = 0; i < Math.min(files.length, 4); i++) {
                    const file = files[i];
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const preview = document.createElement('div');
                            preview.className = 'col-3 mb-2';
                            preview.innerHTML = `
                                <img src="${e.target.result}" class="img-thumbnail" 
                                     style="width: 100%; height: 100px; object-fit: cover;" 
                                     alt="Preview">
                                <small class="text-muted d-block">${file.name}</small>
                            `;
                            previewContainer.appendChild(preview);
                        };
                        reader.readAsDataURL(file);
                    }
                }
                
                if (files.length > 4) {
                    const moreInfo = document.createElement('div');
                    moreInfo.className = 'col-12';
                    moreInfo.innerHTML = `<small class="text-muted">+${files.length - 4} mais arquivo(s)</small>`;
                    previewContainer.appendChild(moreInfo);
                }
            }
        });
    });

    // Search form auto-submit delay
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // Auto-submit could be enabled here if desired
                // searchInput.form.submit();
            }, 500);
        });
    }

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const message = button.getAttribute('data-confirm-delete') || 'Tem certeza que deseja excluir?';
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Schedule conflict warning
    const scheduleForm = document.querySelector('form[action*="schedule"]');
    if (scheduleForm) {
        const roomSelect = scheduleForm.querySelector('#room_id');
        const daySelect = scheduleForm.querySelector('#day_of_week');
        const startTimeInput = scheduleForm.querySelector('#start_time');
        const endTimeInput = scheduleForm.querySelector('#end_time');

        function checkScheduleConflict() {
            if (roomSelect && daySelect && startTimeInput && endTimeInput) {
                const roomId = roomSelect.value;
                const day = daySelect.value;
                const startTime = startTimeInput.value;
                const endTime = endTimeInput.value;

                if (roomId && day !== '' && startTime && endTime) {
                    // Here you could add AJAX call to check for conflicts
                    // For now, just validate that end time > start time
                    if (endTime <= startTime) {
                        endTimeInput.setCustomValidity('O horário de término deve ser posterior ao horário de início.');
                    } else {
                        endTimeInput.setCustomValidity('');
                    }
                }
            }
        }

        if (roomSelect) roomSelect.addEventListener('change', checkScheduleConflict);
        if (daySelect) daySelect.addEventListener('change', checkScheduleConflict);
        if (startTimeInput) startTimeInput.addEventListener('change', checkScheduleConflict);
        if (endTimeInput) endTimeInput.addEventListener('change', checkScheduleConflict);
    }

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                event.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Loading state for forms
    const submitButtons = document.querySelectorAll('form button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.closest('form').addEventListener('submit', function() {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processando...';
            
            // Re-enable after 10 seconds as fallback
            setTimeout(function() {
                button.disabled = false;
                button.innerHTML = button.getAttribute('data-original-text') || 'Enviar';
            }, 10000);
        });
        
        // Store original text
        button.setAttribute('data-original-text', button.innerHTML);
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Ctrl+N for new room
        if (event.ctrlKey && event.key === 'n') {
            event.preventDefault();
            const newRoomLink = document.querySelector('a[href*="room/new"]');
            if (newRoomLink) {
                window.location.href = newRoomLink.href;
            }
        }
        
        // Ctrl+F for search focus
        if (event.ctrlKey && event.key === 'f') {
            const searchInput = document.querySelector('input[name="search"]');
            if (searchInput) {
                event.preventDefault();
                searchInput.focus();
            }
        }
        
        // ESC to close modals
        if (event.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(function(modal) {
                bootstrap.Modal.getInstance(modal).hide();
            });
        }
    });

    // Print functionality
    const printButtons = document.querySelectorAll('[data-print]');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            window.print();
        });
    });

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const text = button.getAttribute('data-copy');
            navigator.clipboard.writeText(text).then(function() {
                // Show feedback
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check me-1"></i>Copiado!';
                setTimeout(function() {
                    button.innerHTML = originalText;
                }, 2000);
            });
        });
    });
});

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertContainer, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            const alert = new bootstrap.Alert(alertContainer);
            alert.close();
        }, 5000);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function validateImageFile(file) {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    const maxSize = 5 * 1024 * 1024; // 5MB
    
    if (!allowedTypes.includes(file.type)) {
        return 'Tipo de arquivo não permitido. Use JPG, PNG ou GIF.';
    }
    
    if (file.size > maxSize) {
        return 'Arquivo muito grande. Tamanho máximo: 5MB.';
    }
    
    return null;
}

// Export for potential use in other scripts
window.MapaDeSalas = {
    showAlert,
    formatFileSize,
    validateImageFile
};
