"""
Modelo de dados para Histórico de Operações
"""
from datetime import datetime
from .database import db
import pytz
from config import active_config

class Historico(db.Model):
    __tablename__ = 'historico'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_operacao = db.Column(db.String(50), nullable=False, index=True)  # 'entrada', 'saida', 'cadastro', etc.
    placa_veiculo = db.Column(db.String(8), nullable=True, index=True)
    numero_vaga = db.Column(db.Integer, nullable=True)
    funcionario_matricula = db.Column(db.String(10), nullable=True)
    funcionario_nome = db.Column(db.String(100), nullable=True)
    tempo_permanencia = db.Column(db.Integer, nullable=True)  # em minutos
    observacoes = db.Column(db.Text, nullable=True)
    data_operacao = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone(active_config.TIMEZONE)), index=True)
    
    def __repr__(self):
        return f'<Historico {self.tipo_operacao}: {self.placa_veiculo or "N/A"} em {self.data_operacao}>'
    
    def to_dict(self):
        """Converte o modelo para dicionário (compatibilidade com JSON)"""
        return {
            'id': self.id,
            'tipo': self.tipo_operacao,
            'placa': self.placa_veiculo,
            'vaga': self.numero_vaga,
            'funcionario_matricula': self.funcionario_matricula,
            'funcionario_nome': self.funcionario_nome,
            'tempo_permanencia': self.tempo_permanencia,
            'observacoes': self.observacoes,
            'data': self.data_operacao.isoformat() if self.data_operacao else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância a partir de um dicionário"""
        data_operacao = None
        if data.get('data'):
            if isinstance(data['data'], str):
                data_operacao = datetime.fromisoformat(data['data'].replace('Z', '+00:00'))
            else:
                data_operacao = data['data']
        
        return cls(
            tipo_operacao=data.get('tipo', data.get('tipo_operacao')),
            placa_veiculo=data.get('placa', data.get('placa_veiculo')),
            numero_vaga=data.get('vaga', data.get('numero_vaga')),
            funcionario_matricula=data.get('funcionario_matricula'),
            funcionario_nome=data.get('funcionario_nome'),
            tempo_permanencia=data.get('tempo_permanencia'),
            observacoes=data.get('observacoes'),
            data_operacao=data_operacao
        )
    
    @staticmethod
    def registrar_entrada(placa, numero_vaga, funcionario_matricula=None, funcionario_nome=None):
        """Registra uma entrada de veículo"""
        historico = Historico(
            tipo_operacao='entrada',
            placa_veiculo=placa.upper(),
            numero_vaga=numero_vaga,
            funcionario_matricula=funcionario_matricula,
            funcionario_nome=funcionario_nome,
            observacoes=f'Veículo {placa.upper()} estacionado na vaga {numero_vaga}'
        )
        historico.salvar()
        return historico
    
    @staticmethod
    def registrar_saida(placa, numero_vaga, tempo_permanencia, funcionario_matricula=None, funcionario_nome=None):
        """Registra uma saída de veículo"""
        historico = Historico(
            tipo_operacao='saida',
            placa_veiculo=placa.upper(),
            numero_vaga=numero_vaga,
            funcionario_matricula=funcionario_matricula,
            funcionario_nome=funcionario_nome,
            tempo_permanencia=tempo_permanencia,
            observacoes=f'Veículo {placa.upper()} saiu da vaga {numero_vaga} após {tempo_permanencia} minutos'
        )
        historico.salvar()
        return historico
    
    @staticmethod
    def registrar_cadastro_veiculo(placa, funcionario_matricula=None, funcionario_nome=None):
        """Registra o cadastro de um veículo"""
        historico = Historico(
            tipo_operacao='cadastro_veiculo',
            placa_veiculo=placa.upper(),
            funcionario_matricula=funcionario_matricula,
            funcionario_nome=funcionario_nome,
            observacoes=f'Veículo {placa.upper()} cadastrado no sistema'
        )
        historico.salvar()
        return historico
    
    @staticmethod
    def registrar_cadastro_funcionario(funcionario_matricula, funcionario_nome):
        """Registra o cadastro de um funcionário"""
        historico = Historico(
            tipo_operacao='cadastro_funcionario',
            funcionario_matricula=funcionario_matricula,
            funcionario_nome=funcionario_nome,
            observacoes=f'Funcionário {funcionario_nome} (matrícula {funcionario_matricula}) cadastrado no sistema'
        )
        historico.salvar()
        return historico
    
    @staticmethod
    def registrar_login(funcionario_matricula, funcionario_nome):
        """Registra o login de um funcionário"""
        historico = Historico(
            tipo_operacao='login',
            funcionario_matricula=funcionario_matricula,
            funcionario_nome=funcionario_nome,
            observacoes=f'Funcionário {funcionario_nome} fez login no sistema'
        )
        historico.salvar()
        return historico
    
    @staticmethod
    def registrar_logout(funcionario_matricula, funcionario_nome):
        """Registra o logout de um funcionário"""
        historico = Historico(
            tipo_operacao='logout',
            funcionario_matricula=funcionario_matricula,
            funcionario_nome=funcionario_nome,
            observacoes=f'Funcionário {funcionario_nome} fez logout do sistema'
        )
        historico.salvar()
        return historico
    
    @staticmethod
    def listar_por_periodo(data_inicio, data_fim):
        """Lista histórico por período"""
        return Historico.query.filter(
            Historico.data_operacao.between(data_inicio, data_fim)
        ).order_by(Historico.data_operacao.desc()).all()
    
    @staticmethod
    def listar_por_placa(placa):
        """Lista histórico de uma placa específica"""
        return Historico.query.filter_by(placa_veiculo=placa.upper()).order_by(Historico.data_operacao.desc()).all()
    
    @staticmethod
    def listar_por_funcionario(matricula):
        """Lista operações de um funcionário específico"""
        return Historico.query.filter_by(funcionario_matricula=matricula).order_by(Historico.data_operacao.desc()).all()
    
    @staticmethod
    def listar_recentes(limit=50):
        """Lista os registros mais recentes"""
        return Historico.query.order_by(Historico.data_operacao.desc()).limit(limit).all()
    
    @staticmethod
    def contar_operacoes_por_tipo():
        """Conta operações por tipo"""
        from sqlalchemy import func
        return db.session.query(
            Historico.tipo_operacao,
            func.count(Historico.id).label('total')
        ).group_by(Historico.tipo_operacao).all()
    
    def salvar(self):
        """Salva o registro na base de dados"""
        db.session.add(self)
        db.session.commit()
    
    def deletar(self):
        """Remove o registro da base de dados"""
        db.session.delete(self)
        db.session.commit()