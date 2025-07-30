"""
Modelo de dados para Veículos
"""
from datetime import datetime
from .database import db
import pytz
from config import active_config

class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(8), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    bloco = db.Column(db.String(10), nullable=True)
    apartamento = db.Column(db.String(10), nullable=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'morador' ou 'visitante'
    data_cadastro = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone(active_config.TIMEZONE)))
    
    # Relacionamento com vagas (um veículo pode estar em uma vaga)
    vaga_ocupada = db.relationship('Vaga', back_populates='veiculo_estacionado', uselist=False)
    
    def __repr__(self):
        return f'<Veiculo {self.placa}: {self.nome}>'
    
    def to_dict(self):
        """Converte o modelo para dicionário (compatibilidade com JSON)"""
        return {
            'id': self.id,
            'placa': self.placa,
            'nome': self.nome,
            'cpf': self.cpf,
            'modelo': self.modelo,
            'bloco': self.bloco,
            'apartamento': self.apartamento,
            'tipo': self.tipo,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância a partir de um dicionário"""
        return cls(
            placa=data['placa'],
            nome=data['nome'],
            cpf=data['cpf'],
            modelo=data['modelo'],
            bloco=data.get('bloco'),
            apartamento=data.get('apartamento'),
            tipo=data['tipo']
        )
    
    @staticmethod
    def buscar_por_placa(placa):
        """Busca um veículo pela placa"""
        return Veiculo.query.filter_by(placa=placa.upper()).first()
    
    @staticmethod
    def listar_todos():
        """Lista todos os veículos ordenados por nome"""
        return Veiculo.query.order_by(Veiculo.nome).all()
    
    @staticmethod
    def contar_por_tipo(tipo):
        """Conta veículos por tipo"""
        return Veiculo.query.filter_by(tipo=tipo).count()
    
    def esta_estacionado(self):
        """Verifica se o veículo está atualmente estacionado"""
        return self.vaga_ocupada is not None
    
    def salvar(self):
        """Salva o veículo na base de dados"""
        db.session.add(self)
        db.session.commit()
    
    def deletar(self):
        """Remove o veículo da base de dados"""
        db.session.delete(self)
        db.session.commit()