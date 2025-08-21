from app import app, db
import models  # importa os modelos para que o SQLAlchemy os conheça

# Garante que as tabelas existem no Postgres (só cria se não existirem)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
