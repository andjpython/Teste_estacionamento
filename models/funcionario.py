"""
Modelo de dados para Funcionários
"""
from datetime import datetime
from .database import db
import pytz
from config import active_config

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(10), unique=True, nullable=False, index=True)
    cargo = db.Column(db.String(50), nullable=True)
    data_cadastro = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone(active_config.TIMEZONE)))
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<Funcionario {self.matricula}: {self.nome}>'
    
    def to_dict(self):
        """Converte o modelo para dicionário (compatibilidade com JSON)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'matricula': self.matricula,
            'cargo': self.cargo,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ativo': self.ativo
        }
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância a partir de um dicionário"""
        return cls(
            nome=data['nome'],
            matricula=data['matricula'],
            cargo=data.get('cargo'),
            ativo=data.get('ativo', True)
        )
    
    @staticmethod
    def buscar_por_matricula(matricula):
        """Busca um funcionário pela matrícula"""
        return Funcionario.query.filter_by(matricula=matricula, ativo=True).first()
    
    @staticmethod
    def listar_ativos():
        """Lista todos os funcionários ativos ordenados por nome"""
        return Funcionario.query.filter_by(ativo=True).order_by(Funcionario.nome).all()
    
    @staticmethod
    def listar_todos():
        """Lista todos os funcionários (ativos e inativos) ordenados por nome"""
        return Funcionario.query.order_by(Funcionario.nome).all()
    
    @staticmethod
    def contar_ativos():
        """Conta funcionários ativos"""
        return Funcionario.query.filter_by(ativo=True).count()
    
    def desativar(self):
        """Desativa o funcionário (soft delete)"""
        self.ativo = False
        db.session.commit()
    
    def ativar(self):
        """Reativa o funcionário"""
        self.ativo = True
        db.session.commit()
    
    def salvar(self):
        """Salva o funcionário na base de dados"""
        db.session.add(self)
        db.session.commit()
    
    def deletar(self):
        """Remove o funcionário da base de dados (hard delete)"""
        db.session.delete(self)
        db.session.commit()