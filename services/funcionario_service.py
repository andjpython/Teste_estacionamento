"""
Serviços para gerenciamento de funcionários
"""
from config import active_config
from models import Funcionario, Historico

def cadastrar_funcionario(nome, matricula, cargo=None):
    """Cadastra um novo funcionário no sistema"""
    # Normalizar dados
    nome = nome.strip() if nome else ""
    matricula = matricula.strip() if matricula else ""
    cargo = cargo.strip() if cargo else None
    
    # Validações
    funcionario_existente = Funcionario.buscar_por_matricula(matricula)
    if funcionario_existente:
        return "❌ Matrícula já cadastrada."
    
    if not matricula or len(matricula) != 4 or not matricula.isdigit():
        return active_config.Mensagens.MATRICULA_INVALIDA
    
    if not nome:
        return "❌ Nome do funcionário é obrigatório."
    
    # Criar e salvar funcionário
    funcionario = Funcionario(
        nome=nome,
        matricula=matricula,
        cargo=cargo
    )
    funcionario.salvar()
    
    # Registrar no histórico
    Historico.registrar_cadastro_funcionario(matricula, nome)
    
    return active_config.Mensagens.FUNCIONARIO_CADASTRADO.format(nome=nome, matricula=matricula)

def listar_funcionarios():
    """Lista todos os funcionários cadastrados"""
    funcionarios = Funcionario.listar_ativos()
    
    if not funcionarios:
        return active_config.Mensagens.NENHUM_FUNCIONARIO_CADASTRADO
    
    linhas = ["📄 FUNCIONÁRIOS CADASTRADOS:"]
    for f in funcionarios:
        cargo_info = f" | Cargo: {f.cargo}" if f.cargo else ""
        linhas.append(f"🔹 Nome: {f.nome} | Matrícula: {f.matricula}{cargo_info}")
    
    return "\n".join(linhas)

def buscar_funcionario_por_matricula(matricula):
    """Busca um funcionário pela matrícula"""
    return Funcionario.buscar_por_matricula(matricula)

def remover_funcionario(matricula):
    """Remove um funcionário do sistema (desativação)"""
    funcionario = Funcionario.buscar_por_matricula(matricula)
    
    if not funcionario:
        return active_config.Mensagens.FUNCIONARIO_NAO_ENCONTRADO
    
    funcionario.desativar()
    return f"✅ Funcionário {funcionario.nome} (matrícula {matricula}) removido com sucesso."

def fazer_login(matricula):
    """Registra login de funcionário"""
    funcionario = Funcionario.buscar_por_matricula(matricula)
    
    if not funcionario:
        return None, active_config.Mensagens.FUNCIONARIO_NAO_ENCONTRADO
    
    # Registrar no histórico
    Historico.registrar_login(matricula, funcionario.nome)
    
    return funcionario, active_config.Mensagens.LOGIN_REALIZADO.format(nome=funcionario.nome)

def fazer_logout(matricula):
    """Registra logout de funcionário"""
    funcionario = Funcionario.buscar_por_matricula(matricula)
    
    if funcionario:
        # Registrar no histórico
        Historico.registrar_logout(matricula, funcionario.nome)
        return active_config.Mensagens.LOGOUT_REALIZADO.format(nome=funcionario.nome)
    
    return "Logout realizado." 