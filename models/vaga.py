"""
Modelo de dados para Vagas
"""
from datetime import datetime
from .database import db
import pytz
from config import active_config

class Vaga(db.Model):
    __tablename__ = 'vagas'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False, index=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'comum' ou 'visitante'
    ocupada = db.Column(db.Boolean, default=False, nullable=False)
    placa_veiculo = db.Column(db.String(8), db.ForeignKey('veiculos.placa'), nullable=True)
    entrada = db.Column(db.DateTime, nullable=True)
    
    # Relacionamento com veículo
    veiculo_estacionado = db.relationship('Veiculo', back_populates='vaga_ocupada')
    
    def __repr__(self):
        return f'<Vaga {self.numero} ({self.tipo}): {"Ocupada" if self.ocupada else "Livre"}>'
    
    def to_dict(self):
        """Converte o modelo para dicionário (compatibilidade com JSON)"""
        return {
            'id': self.id,
            'numero': self.numero,
            'tipo': self.tipo,
            'ocupada': self.ocupada,
            'veiculo': self.placa_veiculo,
            'entrada': self.entrada.isoformat() if self.entrada else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância a partir de um dicionário"""
        entrada = None
        if data.get('entrada'):
            if isinstance(data['entrada'], str):
                entrada = datetime.fromisoformat(data['entrada'].replace('Z', '+00:00'))
            else:
                entrada = data['entrada']
        
        return cls(
            numero=data['numero'],
            tipo=data['tipo'],
            ocupada=data['ocupada'],
            placa_veiculo=data.get('veiculo'),
            entrada=entrada
        )
    
    @staticmethod
    def buscar_por_numero(numero):
        """Busca uma vaga pelo número"""
        return Vaga.query.filter_by(numero=numero).first()
    
    @staticmethod
    def listar_por_tipo(tipo):
        """Lista vagas por tipo"""
        return Vaga.query.filter_by(tipo=tipo).order_by(Vaga.numero).all()
    
    @staticmethod
    def listar_ocupadas():
        """Lista vagas ocupadas"""
        return Vaga.query.filter_by(ocupada=True).order_by(Vaga.numero).all()
    
    @staticmethod
    def listar_livres_por_tipo(tipo):
        """Lista vagas livres de um tipo específico"""
        return Vaga.query.filter_by(tipo=tipo, ocupada=False).order_by(Vaga.numero).all()
    
    @staticmethod
    def contar_ocupadas_por_tipo(tipo):
        """Conta vagas ocupadas por tipo"""
        return Vaga.query.filter_by(tipo=tipo, ocupada=True).count()
    
    @staticmethod
    def contar_livres_por_tipo(tipo):
        """Conta vagas livres por tipo"""
        return Vaga.query.filter_by(tipo=tipo, ocupada=False).count()
    
    def ocupar(self, placa_veiculo):
        """Ocupa a vaga com um veículo"""
        self.ocupada = True
        self.placa_veiculo = placa_veiculo.upper()
        self.entrada = datetime.now(pytz.timezone(active_config.TIMEZONE))
        db.session.commit()
    
    def liberar(self):
        """Libera a vaga"""
        self.ocupada = False
        self.placa_veiculo = None
        self.entrada = None
        db.session.commit()
    
    def tempo_ocupacao_minutos(self):
        """Retorna o tempo de ocupação em minutos"""
        if not self.ocupada or not self.entrada:
            return 0
        
        agora = datetime.now(pytz.timezone(active_config.TIMEZONE))
        if self.entrada.tzinfo is None:
            self.entrada = pytz.timezone(active_config.TIMEZONE).localize(self.entrada)
        
        diferenca = agora - self.entrada
        return diferenca.total_seconds() / 60
    
    def tempo_restante_minutos(self):
        """Retorna o tempo restante em minutos"""
        if not self.ocupada:
            return 0
        
        limite_minutos = active_config.LIMITE_HORAS_ESTACIONAMENTO * 60
        tempo_ocupado = self.tempo_ocupacao_minutos()
        return max(0, limite_minutos - tempo_ocupado)
    
    def esta_no_limite(self):
        """Verifica se a vaga está no limite de tempo"""
        return self.tempo_restante_minutos() <= 0
    
    def salvar(self):
        """Salva a vaga na base de dados"""
        db.session.add(self)
        db.session.commit()
    
    def deletar(self):
        """Remove a vaga da base de dados"""
        db.session.delete(self)
        db.session.commit()