"""
Configuração da base de dados SQLAlchemy
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instância do SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Inicializa a base de dados com a aplicação Flask"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Importar todos os modelos para que sejam registrados
        from . import veiculo, vaga, funcionario, historico
        
        # Criar as tabelas se não existirem
        db.create_all()
        
        # Inicializar dados padrão se necessário
        _inicializar_dados_padrao()

def _inicializar_dados_padrao():
    """Inicializa dados padrão como vagas se não existirem"""
    from .vaga import Vaga
    from config import active_config
    
    # Verificar se já existem vagas
    if Vaga.query.count() == 0:
        print("Criando vagas padrão...")
        
        # Criar vagas comuns
        for i in range(active_config.VAGAS_COMUNS):
            vaga = Vaga(
                numero=i + 1,
                tipo='comum',
                ocupada=False
            )
            db.session.add(vaga)
        
        # Criar vagas de visitantes
        for i in range(active_config.VAGAS_VISITANTES):
            vaga = Vaga(
                numero=i + active_config.VAGAS_COMUNS + 1,
                tipo='visitante',
                ocupada=False
            )
            db.session.add(vaga)
        
        db.session.commit()
        print(f"Criadas {active_config.VAGAS_COMUNS + active_config.VAGAS_VISITANTES} vagas")