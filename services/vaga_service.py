from datetime import datetime
import pytz
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Listar status das vagas ===
def ver_status_vagas(vagas):
    if not vagas:
        return "📭 Nenhuma vaga cadastrada."
    
    status = ["📋 STATUS DAS VAGAS:"]
    for v in vagas:
        s = "🟢 Livre" if not v["ocupada"] else f"🔴 Ocupada por {v['veiculo']}"
        status.append(f"Vaga {v['numero']} ({v['tipo']}): {s}")
    
    return "\n".join(status)

# === Verificar tempo excedido ===
def verificar_tempo_excedido(vagas, limite_horas=72):
    try:
        agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
        excedidos = []
        
        for v in vagas:
            if v['ocupada'] and v['entrada']:
                try:
                    entrada = datetime.fromisoformat(v['entrada'])
                    horas = (agora - entrada).total_seconds() / 3600
                    
                    if horas > limite_horas:
                        excedidos.append({
                            'numero': v['numero'],
                            'tipo': v['tipo'],
                            'veiculo': v['veiculo'],
                            'horas': round(horas, 1)
                        })
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Erro ao processar data de entrada da vaga {v.get('numero', '?')}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Erro inesperado ao processar vaga {v.get('numero', '?')}: {e}")
                    continue
        
        return excedidos
        
    except Exception as e:
        logger.error(f"Erro ao verificar tempo excedido: {e}")
        return [] 