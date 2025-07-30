import re
from datetime import datetime
import pytz
from config import active_config
from models import Veiculo, Historico

# === Funções de validação ===
def validar_placa(placa):
    """Valida placa nos formatos antigo (ABC1234) e Mercosul (ABC1D23)"""
    if not placa:
        return False
    
    placa = placa.replace(" ", "").upper()
    
    # Padrão antigo: ABC1234
    padrao_antigo = re.match(r'^[A-Z]{3}[0-9]{4}$', placa)
    # Padrão Mercosul: ABC1D23
    padrao_mercosul = re.match(r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$', placa)
    
    return bool(padrao_antigo or padrao_mercosul)

def validar_cpf(cpf):
    """Valida CPF com algoritmo de verificação dos dígitos"""
    if not cpf:
        return False
    
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se não são todos iguais (ex: 111.111.111-11)
    if cpf == cpf[0] * 11:
        return False
    
    # Validação dos dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[j]) * ((i + 1) - j) for j in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            return False
    
    return True

def normalizar_cpf(cpf):
    """Normaliza CPF removendo formatação"""
    if not cpf:
        return ""
    return re.sub(r'\D', '', cpf.strip())

def normalizar_placa(placa):
    """Normaliza placa removendo espaços e convertendo para maiúscula"""
    if not placa:
        return ""
    return placa.replace(" ", "").upper().strip()

# === Cadastro de veículo ===
def cadastrar_veiculo(placa, cpf, modelo, nome, bloco, apartamento, funcionario_matricula=None, funcionario_nome=None):
    # Normalizar dados de entrada
    placa = normalizar_placa(placa)
    cpf = normalizar_cpf(cpf)
    nome = nome.strip() if nome else ""
    modelo = modelo.strip() if modelo else ""
    bloco = bloco.strip() if bloco else ""
    apartamento = apartamento.strip() if apartamento else ""
    
    # Validações
    veiculo_existente = Veiculo.buscar_por_placa(placa)
    if veiculo_existente:
        return active_config.Mensagens.VEICULO_JA_CADASTRADO
    
    if not validar_placa(placa):
        return active_config.Mensagens.PLACA_INVALIDA
    
    if not validar_cpf(cpf):
        return active_config.Mensagens.CPF_INVALIDO
    
    if not nome:
        return active_config.Mensagens.NOME_OBRIGATORIO
    
    # Determinar tipo baseado no modelo
    tipo = "morador" if modelo else "visitante"
    
    # Criar e salvar veículo
    veiculo = Veiculo(
        placa=placa,
        cpf=cpf,
        modelo=modelo,
        tipo=tipo,
        nome=nome,
        bloco=bloco,
        apartamento=apartamento
    )
    veiculo.salvar()
    
    # Registrar no histórico
    Historico.registrar_cadastro_veiculo(placa, funcionario_matricula, funcionario_nome)
    
    return active_config.Mensagens.VEICULO_CADASTRADO.format(placa=placa, tipo=tipo)

# === Listar veículos cadastrados ===
def listar_veiculos_cadastrados():
    """Lista todos os veículos cadastrados no sistema"""
    veiculos = Veiculo.listar_todos()
    
    if not veiculos:
        return active_config.Mensagens.NENHUM_VEICULO_CADASTRADO
    
    linhas = ["📄 VEÍCULOS CADASTRADOS:"]
    for v in veiculos:
        linhas.append(
            f"🔹 Placa: {v.placa} | Nome: {v.nome} | Tipo: {v.tipo.capitalize()} | "
            f"CPF: {v.cpf} | Modelo: {v.modelo or 'N/A'} | "
            f"Bloco: {v.bloco} | Apto: {v.apartamento}"
        )
    return "\n".join(linhas)

# === Buscar veículo por placa ===
def buscar_veiculo_por_placa(placa):
    """Busca um veículo pela placa"""
    placa_normalizada = normalizar_placa(placa)
    return Veiculo.buscar_por_placa(placa_normalizada)

# === Remover veículo ===
def remover_veiculo(placa):
    """Remove um veículo do sistema"""
    placa_normalizada = normalizar_placa(placa)
    veiculo = Veiculo.buscar_por_placa(placa_normalizada)
    
    if not veiculo:
        return active_config.Mensagens.VEICULO_NAO_CADASTRADO
    
    # Verificar se o veículo está estacionado
    if veiculo.esta_estacionado():
        return f"❌ Não é possível remover o veículo {placa_normalizada} pois está estacionado."
    
    veiculo.deletar()
    return f"✅ Veículo {placa_normalizada} removido com sucesso." 