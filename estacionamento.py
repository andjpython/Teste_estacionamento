import os
import json
from datetime import datetime
import re
from supervisor import menu_supervisor
import pytz
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Caminhos dos Arquivos ===
DADOS_DIR = "dados"
VEICULOS_PATH = os.path.join(DADOS_DIR, "veiculos.json")
VAGAS_PATH = os.path.join(DADOS_DIR, "vagas.json")
HISTORICO_PATH = os.path.join(DADOS_DIR, "historico.json")
FUNCIONARIOS_PATH = os.path.join(DADOS_DIR, "funcionarios.json")

# === Inicialização dos arquivos ===
def inicializar_arquivos():
    try:
        os.makedirs(DADOS_DIR, exist_ok=True)
        
        if not os.path.exists(VEICULOS_PATH):
            with open(VEICULOS_PATH, "w", encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
                
        if not os.path.exists(VAGAS_PATH):
            vagas = [
                {"numero": i + 1, "tipo": "comum", "ocupada": False, "veiculo": None, "entrada": None}
                for i in range(20)
            ] + [
                {"numero": i + 21, "tipo": "visitante", "ocupada": False, "veiculo": None, "entrada": None}
                for i in range(10)
            ]
            with open(VAGAS_PATH, "w", encoding='utf-8') as f:
                json.dump(vagas, f, ensure_ascii=False, indent=4)
                
        if not os.path.exists(HISTORICO_PATH):
            with open(HISTORICO_PATH, "w", encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
                
        if not os.path.exists(FUNCIONARIOS_PATH):
            with open(FUNCIONARIOS_PATH, "w", encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
                
        logger.info("Arquivos de dados inicializados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar arquivos: {e}")
        raise

def carregar_dados():
    try:
        inicializar_arquivos()
        
        with open(VEICULOS_PATH, 'r', encoding='utf-8') as f:
            veiculos = json.load(f)
        with open(VAGAS_PATH, 'r', encoding='utf-8') as f:
            vagas = json.load(f)
        with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
            historico = json.load(f)
        with open(FUNCIONARIOS_PATH, 'r', encoding='utf-8') as f:
            funcionarios = json.load(f)
            
        return veiculos, vagas, historico, funcionarios
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Erro ao carregar dados: {e}")
        # Retorna dados vazios se houver erro
        return [], [], [], []
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar dados: {e}")
        return [], [], [], []

def salvar_dados(veiculos, vagas, historico, funcionarios):
    try:
        with open(VEICULOS_PATH, 'w', encoding='utf-8') as f:
            json.dump(veiculos, f, indent=4, ensure_ascii=False)
        with open(VAGAS_PATH, 'w', encoding='utf-8') as f:
            json.dump(vagas, f, indent=4, default=str, ensure_ascii=False)
        with open(HISTORICO_PATH, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=4, default=str, ensure_ascii=False)
        with open(FUNCIONARIOS_PATH, 'w', encoding='utf-8') as f:
            json.dump(funcionarios, f, indent=4, ensure_ascii=False)
            
        logger.debug("Dados salvos com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao salvar dados: {e}")
        raise

# === Validações ===
def validar_cpf(cpf):
    if not cpf:
        return False
    
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
        
    for i in [9, 10]:
        soma = sum(int(cpf[j]) * ((i+1) - j) for j in range(i))
        dig = (soma * 10 % 11) % 10
        if dig != int(cpf[i]):
            return False
    return True

def validar_placa(placa):
    if not placa:
        return False
    
    placa_clean = placa.replace(" ", "").upper()
    # Padrão antigo (ABC1234) ou Mercosul (ABC1D23)
    return bool(re.match(r'^[A-Z]{3}[0-9]{4}$', placa_clean) or 
                re.match(r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$', placa_clean))

def normalizar_placa(placa):
    """Normaliza placa removendo espaços e convertendo para maiúscula"""
    if not placa:
        return ""
    return placa.replace(" ", "").upper().strip()

# === Cadastro de veículo ===
# Função removida - agora importada de services.veiculo_service

# === Estacionamento ===
def estacionar_veiculo(placa, veiculos, vagas, historico):
    try:
        placa = normalizar_placa(placa)
        veiculo = next((v for v in veiculos if v['placa'] == placa), None)
        
        if not veiculo:
            return "❌ Veículo não cadastrado."
            
        if any(v['veiculo'] == placa for v in vagas if v['ocupada']):
            return "⚠️ Este veículo já está estacionado."
            
        tipo_vaga = "comum" if veiculo["tipo"] == "morador" else "visitante"
        
        for vaga in vagas:
            if not vaga["ocupada"] and vaga["tipo"] == tipo_vaga:
                vaga["ocupada"] = True
                vaga["veiculo"] = placa
                vaga["entrada"] = datetime.now(pytz.timezone("America/Sao_Paulo")).isoformat()
                
                historico.append({
                    "acao": "entrada_veiculo",
                    "placa": placa,
                    "nome": veiculo["nome"],
                    "tipo": veiculo["tipo"],
                    "vaga": vaga["numero"],
                    "data": vaga["entrada"]
                })
                
                logger.info(f"Veículo {placa} estacionado na vaga {vaga['numero']}")
                return f"✅ Veículo {placa} estacionado na vaga {vaga['numero']} ({tipo_vaga})."
                
        return f"🚫 Nenhuma vaga disponível para tipo {tipo_vaga}."
        
    except Exception as e:
        logger.error(f"Erro ao estacionar veículo {placa}: {e}")
        return "❌ Erro interno ao estacionar veículo."

# === Estacionar por dados (agora só por placa) ===
def estacionar_veiculo_por_dados(placa, veiculos, vagas, historico):
    placa = normalizar_placa(placa)
    veiculo = next((v for v in veiculos if v['placa'] == placa), None)
    
    if not veiculo:
        return "❌ Veículo não cadastrado. Faça o cadastro primeiro."
        
    return estacionar_veiculo(placa, veiculos, vagas, historico)

# === Liberação de vaga ===
def liberar_vaga(placa, matricula, veiculos, vagas, historico, funcionarios):
    try:
        placa = normalizar_placa(placa)
        vaga = next((v for v in vagas if v["ocupada"] and v["veiculo"] == placa), None)
        veiculo = next((v for v in veiculos if v["placa"] == placa), None)
        funcionario = next((f for f in funcionarios if f["matricula"] == matricula), None)
        
        if not vaga:
            return "❌ Veículo não encontrado em nenhuma vaga ocupada."
        if not veiculo:
            return "❌ Veículo não cadastrado no sistema."
        if not funcionario:
            return "❌ Matrícula de funcionário inválida."
            
        try:
            entrada = datetime.fromisoformat(vaga["entrada"])
            saida = datetime.now(pytz.timezone("America/Sao_Paulo"))
            tempo = (saida - entrada).total_seconds() / 60
        except (ValueError, TypeError) as e:
            logger.warning(f"Erro ao processar data de entrada para vaga {vaga['numero']}: {e}")
            tempo = 0
            
        historico.append({
            "acao": "saida_veiculo",
            "placa": placa,
            "nome": veiculo["nome"],
            "vaga": vaga["numero"],
            "tempo_min": round(tempo),
            "funcionario": funcionario["nome"],
            "matricula": matricula,
            "data_saida": saida.isoformat()
        })
        
        vaga["ocupada"] = False
        vaga["veiculo"] = None
        vaga["entrada"] = None
        
        logger.info(f"Veículo {placa} liberado da vaga {vaga['numero']} por {funcionario['nome']}")
        return f"✅ Veículo {placa} saiu da vaga {vaga['numero']}. Tempo: {round(tempo)} min."
        
    except Exception as e:
        logger.error(f"Erro ao liberar vaga para veículo {placa}: {e}")
        return "❌ Erro interno ao liberar vaga."

# === Relatórios ===
# Função removida - agora importada de services.vaga_service

# Função removida - agora importada de services.vaga_service

# === Remoção por CPF ===
def remover_veiculo_por_cpf(cpf, matricula, veiculos, vagas, historico, funcionarios):
    try:
        # Normalizar CPF
        cpf_normalizado = re.sub(r'\D', '', cpf.strip())
        
        veiculo = next((v for v in veiculos if re.sub(r'\D', '', v["cpf"]) == cpf_normalizado), None)
        funcionario = next((f for f in funcionarios if f["matricula"] == matricula), None)
        
        if not veiculo:
            return "❌ Nenhum veículo encontrado com este CPF."
        if not funcionario:
            return "❌ Matrícula inválida."
            
        placa = veiculo["placa"]
        vaga = next((v for v in vagas if v["ocupada"] and v["veiculo"] == placa), None)
        
        # Liberar vaga se estiver ocupada
        if vaga:
            vaga["ocupada"] = False
            vaga["veiculo"] = None
            vaga["entrada"] = None
            
        veiculos.remove(veiculo)
        
        historico.append({
            "acao": "remocao_manual",
            "placa": placa,
            "cpf": cpf_normalizado,
            "funcionario": funcionario["nome"],
            "matricula": matricula,
            "data": datetime.now(pytz.timezone("America/Sao_Paulo")).isoformat()
        })
        
        logger.info(f"Veículo {placa} removido por CPF {cpf_normalizado} por {funcionario['nome']}")
        return f"🗑️ Veículo {placa} removido por {funcionario['nome']}."
        
    except Exception as e:
        logger.error(f"Erro ao remover veículo por CPF {cpf}: {e}")
        return "❌ Erro interno ao remover veículo."

# === Funcionários ===
# Função removida - agora importada de services.funcionario_service

# Função removida - agora importada de services.funcionario_service

def registrar_entrada(matricula, funcionarios, historico):
    try:
        funcionario = next((f for f in funcionarios if f['matricula'] == matricula), None)
        if not funcionario:
            return "❌ Matrícula não encontrada."
            
        historico.append({
            "acao": "login",
            "matricula": matricula,
            "nome": funcionario['nome'],
            "data": datetime.now(pytz.timezone("America/Sao_Paulo")).isoformat()
        })
        
        logger.info(f"Login registrado para funcionário {funcionario['nome']}")
        return f"🔓 Funcionário {funcionario['nome']} entrou."
        
    except Exception as e:
        logger.error(f"Erro ao registrar entrada do funcionário {matricula}: {e}")
        return "❌ Erro interno ao registrar entrada."

def registrar_saida(matricula, funcionarios, historico):
    try:
        funcionario = next((f for f in funcionarios if f['matricula'] == matricula), None)
        if not funcionario:
            return "❌ Matrícula não encontrada."
            
        historico.append({
            "acao": "logout",
            "matricula": matricula,
            "nome": funcionario['nome'],
            "data": datetime.now(pytz.timezone("America/Sao_Paulo")).isoformat()
        })
        
        logger.info(f"Logout registrado para funcionário {funcionario['nome']}")
        return f"🔒 Funcionário {funcionario['nome']} saiu."
        
    except Exception as e:
        logger.error(f"Erro ao registrar saída do funcionário {matricula}: {e}")
        return "❌ Erro interno ao registrar saída."

# === Listagem de veículos ===
# Função removida - agora importada de services.veiculo_service

# === Menu Terminal (modo interativo) ===
def menu():
    inicializar_arquivos()
    veiculos, vagas, historico, funcionarios = carregar_dados()
    while True:
        print("\n==== MENU ESTACIONAMENTO ====")
        print("0. Área do Supervisor 🔐")
        print("1. Cadastrar veículo")
        print("2. Estacionar veículo")
        print("3. Registrar saída")
        print("4. Ver status de vagas")
        print("5. Verificar tempo excedido")
        print("6. Remover veículo por CPF")
        print("7. Cadastrar funcionário")
        print("8. Listar funcionários")
        print("9. Login funcionário")
        print("10. Logout funcionário")
        print("11. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            from supervisor import menu_supervisor
            from services.funcionario_service import cadastrar_funcionario, listar_funcionarios
            from services.veiculo_service import listar_veiculos_cadastrados
            menu_supervisor(carregar_dados, salvar_dados, cadastrar_funcionario, listar_funcionarios, listar_veiculos_cadastrados)
        elif opcao == "1":
            from services.veiculo_service import cadastrar_veiculo
            placa = input("Placa: ").strip().upper()
            cpf = input("CPF: ").strip()
            modelo = input("Modelo (deixe vazio se visitante): ").strip()
            nome = input("Nome: ").strip()
            bloco = input("Bloco: ").strip()
            apartamento = input("Apartamento: ").strip()
            print(cadastrar_veiculo(veiculos, placa, cpf, modelo, nome, bloco, apartamento))
        elif opcao == "2":
            placa = input("Digite a placa do veículo: ").strip()
            print(estacionar_veiculo(placa, veiculos, vagas, historico))
        elif opcao == "3":
            placa = input("Placa do veículo: ").strip()
            matricula = input("Matrícula do funcionário: ").strip()
            print(liberar_vaga(placa, matricula, veiculos, vagas, historico, funcionarios))
        elif opcao == "4":
            from services.vaga_service import ver_status_vagas
            print(ver_status_vagas(vagas))
        elif opcao == "5":
            from services.vaga_service import verificar_tempo_excedido
            print(verificar_tempo_excedido(vagas))
        elif opcao == "6":
            cpf = input("CPF do proprietário: ").strip()
            matricula = input("Matrícula do funcionário: ").strip()
            print(remover_veiculo_por_cpf(cpf, matricula, veiculos, vagas, historico, funcionarios))
        elif opcao == "7":
            from services.funcionario_service import cadastrar_funcionario
            nome = input("Nome do funcionário: ").strip()
            matricula = input("Matrícula (4 dígitos): ").strip()
            print(cadastrar_funcionario(funcionarios, nome, matricula))
        elif opcao == "8":
            from services.funcionario_service import listar_funcionarios
            print(listar_funcionarios(funcionarios))
        elif opcao == "9":
            matricula = input("Digite sua matrícula: ").strip()
            print(registrar_entrada(matricula, funcionarios, historico))
        elif opcao == "10":
            matricula = input("Digite sua matrícula: ").strip()
            print(registrar_saida(matricula, funcionarios, historico))
        elif opcao == "11":
            salvar_dados(veiculos, vagas, historico, funcionarios)
            print("🚪 Saindo... Até logo!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    menu()
