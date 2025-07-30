"""
Serviços para gerenciamento de histórico
"""
from datetime import datetime, timedelta
import pytz
from config import active_config
from models import Historico

# === Ver histórico completo ===
def ver_historico(limit=50):
    """Lista o histórico de operações"""
    registros = Historico.listar_recentes(limit)
    
    if not registros:
        return "📭 Nenhum registro no histórico."
    
    linhas = ["📊 HISTÓRICO DE OPERAÇÕES:"]
    for h in registros:
        data_formatada = h.data_operacao.strftime("%d/%m/%Y %H:%M") if h.data_operacao else "N/A"
        placa_info = f" - {h.placa_veiculo}" if h.placa_veiculo else ""
        funcionario_info = f" - {h.funcionario_nome}" if h.funcionario_nome else ""
        
        linhas.append(
            f"🔹 {data_formatada}: {h.tipo_operacao.upper()}{placa_info}{funcionario_info}"
        )
    
    return "\n".join(linhas)

# === Filtrar histórico por matrícula ===
def filtrar_historico_por_matricula(matricula, limit=50):
    """Filtra histórico por matrícula de funcionário"""
    registros = Historico.listar_por_funcionario(matricula)[:limit]
    
    if not registros:
        return f"📭 Nenhum registro encontrado para a matrícula {matricula}."
    
    linhas = [f"📊 HISTÓRICO DA MATRÍCULA {matricula}:"]
    for h in registros:
        data_formatada = h.data_operacao.strftime("%d/%m/%Y %H:%M") if h.data_operacao else "N/A"
        placa_info = f" - {h.placa_veiculo}" if h.placa_veiculo else ""
        
        linhas.append(
            f"🔹 {data_formatada}: {h.tipo_operacao.upper()}{placa_info}"
        )
    
    return "\n".join(linhas)

# === Filtrar histórico por placa ===
def filtrar_historico_por_placa(placa, limit=20):
    """Filtra histórico por placa de veículo"""
    registros = Historico.listar_por_placa(placa)[:limit]
    
    if not registros:
        return f"📭 Nenhum registro encontrado para a placa {placa}."
    
    linhas = [f"📊 HISTÓRICO DA PLACA {placa}:"]
    for h in registros:
        data_formatada = h.data_operacao.strftime("%d/%m/%Y %H:%M") if h.data_operacao else "N/A"
        funcionario_info = f" - {h.funcionario_nome}" if h.funcionario_nome else ""
        tempo_info = f" ({h.tempo_permanencia} min)" if h.tempo_permanencia else ""
        
        linhas.append(
            f"🔹 {data_formatada}: {h.tipo_operacao.upper()}{funcionario_info}{tempo_info}"
        )
    
    return "\n".join(linhas)

# === Relatório de operações por período ===
def relatorio_por_periodo(data_inicio, data_fim):
    """Gera relatório de operações por período"""
    try:
        if isinstance(data_inicio, str):
            data_inicio = datetime.fromisoformat(data_inicio)
        if isinstance(data_fim, str):
            data_fim = datetime.fromisoformat(data_fim)
        
        registros = Historico.listar_por_periodo(data_inicio, data_fim)
        
        if not registros:
            return f"📭 Nenhuma operação encontrada entre {data_inicio.strftime('%d/%m/%Y')} e {data_fim.strftime('%d/%m/%Y')}."
        
        # Agrupar por tipo de operação
        operacoes_por_tipo = {}
        for h in registros:
            tipo = h.tipo_operacao
            if tipo not in operacoes_por_tipo:
                operacoes_por_tipo[tipo] = []
            operacoes_por_tipo[tipo].append(h)
        
        linhas = [
            f"📊 RELATÓRIO DE OPERAÇÕES",
            f"📅 Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
            f"📈 Total de operações: {len(registros)}",
            ""
        ]
        
        for tipo, operacoes in operacoes_por_tipo.items():
            linhas.append(f"🔹 {tipo.upper()}: {len(operacoes)} operações")
        
        return "\n".join(linhas)
        
    except Exception as e:
        return f"❌ Erro ao gerar relatório: {e}"

# === Estatísticas do histórico ===
def obter_estatisticas_historico():
    """Retorna estatísticas do histórico"""
    try:
        # Contar operações por tipo
        operacoes_por_tipo = Historico.contar_operacoes_por_tipo()
        
        # Operações dos últimos 7 dias
        uma_semana_atras = datetime.now(pytz.timezone(active_config.TIMEZONE)) - timedelta(days=7)
        operacoes_recentes = Historico.listar_por_periodo(
            uma_semana_atras, 
            datetime.now(pytz.timezone(active_config.TIMEZONE))
        )
        
        stats = {
            'total_operacoes': sum(count for _, count in operacoes_por_tipo),
            'operacoes_por_tipo': dict(operacoes_por_tipo),
            'operacoes_ultima_semana': len(operacoes_recentes)
        }
        
        return stats
        
    except Exception as e:
        return {'erro': str(e)}

# === Limpar histórico antigo ===
def limpar_historico_antigo(dias_para_manter=90):
    """Remove registros de histórico mais antigos que o número especificado de dias"""
    try:
        data_limite = datetime.now(pytz.timezone(active_config.TIMEZONE)) - timedelta(days=dias_para_manter)
        
        # Contar registros que serão removidos
        registros_antigos = Historico.query.filter(Historico.data_operacao < data_limite).all()
        total_removidos = len(registros_antigos)
        
        # Remover registros
        for registro in registros_antigos:
            registro.deletar()
        
        return f"✅ {total_removidos} registros antigos removidos (anteriores a {data_limite.strftime('%d/%m/%Y')})."
        
    except Exception as e:
        return f"❌ Erro ao limpar histórico: {e}" 