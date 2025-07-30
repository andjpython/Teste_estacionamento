from datetime import datetime
import pytz
from config import active_config
from models import Vaga, Veiculo, Historico
from utils.logging_config import setup_logger, log_error

# Configurar logger
logger = setup_logger(__name__)

# === Listar status das vagas ===
def ver_status_vagas():
    """Retorna o status atual de todas as vagas"""
    vagas = Vaga.query.order_by(Vaga.numero).all()
    
    if not vagas:
        return active_config.Mensagens.NENHUMA_VAGA_CADASTRADA
    
    status = ["📋 STATUS DAS VAGAS:"]
    for v in vagas:
        s = "🟢 Livre" if not v.ocupada else f"🔴 Ocupada por {v.placa_veiculo}"
        status.append(f"Vaga {v.numero} ({v.tipo}): {s}")
    
    return "\n".join(status)

# === Verificar tempo excedido ===
def verificar_tempo_excedido(limite_horas=None):
    """Verifica quais veículos excederam o tempo limite de estacionamento"""
    try:
        if limite_horas is None:
            limite_horas = active_config.LIMITE_HORAS_ESTACIONAMENTO
            
        vagas_ocupadas = Vaga.listar_ocupadas()
        excedidos = []
        
        for vaga in vagas_ocupadas:
            if vaga.esta_no_limite():
                tempo_ocupacao = vaga.tempo_ocupacao_minutos()
                excedidos.append({
                    'numero': vaga.numero,
                    'tipo': vaga.tipo,
                    'veiculo': vaga.placa_veiculo,
                    'horas': round(tempo_ocupacao / 60, 1)
                })
        
        return excedidos
        
    except Exception as e:
        log_error(logger, e, "verificação de tempo excedido")
        return []

# === Estacionar veículo ===
def estacionar_veiculo(placa, funcionario_matricula=None, funcionario_nome=None):
    """Estaciona um veículo em uma vaga disponível"""
    try:
        # Verificar se o veículo está cadastrado
        veiculo = Veiculo.buscar_por_placa(placa)
        if not veiculo:
            return active_config.Mensagens.VEICULO_NAO_CADASTRADO
        
        # Verificar se já está estacionado
        if veiculo.esta_estacionado():
            return active_config.Mensagens.VEICULO_JA_ESTACIONADO
        
        # Buscar vaga disponível do tipo correto
        tipo_vaga = "comum" if veiculo.tipo == "morador" else "visitante"
        vagas_livres = Vaga.listar_livres_por_tipo(tipo_vaga)
        
        if not vagas_livres:
            return active_config.Mensagens.VAGA_NAO_DISPONIVEL.format(tipo=tipo_vaga)
        
        # Ocupar a primeira vaga disponível
        vaga = vagas_livres[0]
        vaga.ocupar(placa)
        
        # Registrar no histórico
        Historico.registrar_entrada(placa, vaga.numero, funcionario_matricula, funcionario_nome)
        
        return active_config.Mensagens.VEICULO_ESTACIONADO.format(
            placa=placa, numero=vaga.numero, tipo=tipo_vaga
        )
        
    except Exception as e:
        log_error(logger, e, f"estacionamento do veículo {placa}")
        return active_config.Mensagens.ERRO_INTERNO

# === Liberar vaga ===
def liberar_vaga(numero_vaga, funcionario_matricula=None, funcionario_nome=None):
    """Libera uma vaga ocupada"""
    try:
        vaga = Vaga.buscar_por_numero(numero_vaga)
        if not vaga:
            return f"❌ Vaga {numero_vaga} não encontrada."
        
        if not vaga.ocupada:
            return f"❌ Vaga {numero_vaga} já está livre."
        
        # Calcular tempo de permanência
        tempo_permanencia = int(vaga.tempo_ocupacao_minutos())
        placa = vaga.placa_veiculo
        
        # Liberar vaga
        vaga.liberar()
        
        # Registrar no histórico
        Historico.registrar_saida(placa, numero_vaga, tempo_permanencia, 
                                funcionario_matricula, funcionario_nome)
        
        return active_config.Mensagens.VEICULO_LIBERADO.format(
            placa=placa, numero=numero_vaga, tempo=tempo_permanencia
        )
        
    except Exception as e:
        log_error(logger, e, f"liberação da vaga {numero_vaga}")
        return active_config.Mensagens.ERRO_INTERNO

# === Buscar vaga por placa ===
def buscar_vaga_por_placa(placa):
    """Busca a vaga ocupada por uma placa específica"""
    return Vaga.query.filter_by(placa_veiculo=placa.upper(), ocupada=True).first()

# === Estatísticas das vagas ===
def obter_estatisticas_vagas():
    """Retorna estatísticas das vagas"""
    try:
        stats = {
            'total_vagas': Vaga.query.count(),
            'vagas_ocupadas': Vaga.query.filter_by(ocupada=True).count(),
            'vagas_livres': Vaga.query.filter_by(ocupada=False).count(),
            'comuns_ocupadas': Vaga.contar_ocupadas_por_tipo('comum'),
            'comuns_livres': Vaga.contar_livres_por_tipo('comum'),
            'visitantes_ocupadas': Vaga.contar_ocupadas_por_tipo('visitante'),
            'visitantes_livres': Vaga.contar_livres_por_tipo('visitante')
        }
        return stats
    except Exception as e:
        log_error(logger, e, "obtenção de estatísticas das vagas")
        return {} 