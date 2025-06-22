import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import re
from supervisor import menu_supervisor
import os
from datetime import datetime, timezone, timedelta
br_tz = timezone(timedelta(hours=-3))
datetime.now(br_tz)

# === Caminhos dos Arquivos ===
DADOS_DIR = "dados"
VEICULOS_PATH = os.path.join(DADOS_DIR, "veiculos.json")
VAGAS_PATH = os.path.join(DADOS_DIR, "vagas.json")
HISTORICO_PATH = os.path.join(DADOS_DIR, "historico.json")
FUNCIONARIOS_PATH = os.path.join(DADOS_DIR, "funcionarios.json")

# === Inicialização dos arquivos ===
def inicializar_arquivos():
    os.makedirs(DADOS_DIR, exist_ok=True)
    if not os.path.exists(VEICULOS_PATH):
        with open(VEICULOS_PATH, "w") as f:
            json.dump([], f)
    if not os.path.exists(VAGAS_PATH):
        vagas = [
            {"numero": i + 1, "tipo": "comum", "ocupada": False, "veiculo": None, "entrada": None}
            for i in range(20)
        ] + [
            {"numero": i + 21, "tipo": "visitante", "ocupada": False, "veiculo": None, "entrada": None}
            for i in range(10)
        ]
        with open(VAGAS_PATH, "w") as f:
            json.dump(vagas, f)
    if not os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, "w") as f:
            json.dump([], f)
    if not os.path.exists(FUNCIONARIOS_PATH):
        with open(FUNCIONARIOS_PATH, "w") as f:
            json.dump([], f)

def carregar_dados():
    with open(VEICULOS_PATH, 'r') as f:
        veiculos = json.load(f)
    with open(VAGAS_PATH, 'r') as f:
        vagas = json.load(f)
    with open(HISTORICO_PATH, 'r') as f:
        historico = json.load(f)
    with open(FUNCIONARIOS_PATH, 'r') as f:
        funcionarios = json.load(f)
    return veiculos, vagas, historico, funcionarios

def salvar_dados(veiculos, vagas, historico, funcionarios):
    with open(VEICULOS_PATH, 'w') as f:
        json.dump(veiculos, f, indent=4)
    with open(VAGAS_PATH, 'w') as f:
        json.dump(vagas, f, indent=4, default=str)
    with open(HISTORICO_PATH, 'w') as f:
        json.dump(historico, f, indent=4, default=str)
    with open(FUNCIONARIOS_PATH, 'w') as f:
        json.dump(funcionarios, f, indent=4)

# === Validações ===
def validar_cpf(cpf):
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
    return bool(re.match(r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$', placa.upper()))

# === Cadastro de veículo ===
def cadastrar_veiculo(veiculos, placa, cpf, modelo, nome, bloco, apartamento):
    if any(v['placa'] == placa.upper() for v in veiculos):
        return "❌ Veículo já cadastrado com essa placa."
    if not validar_placa(placa):
        return "❌ Placa inválida."
    if not validar_cpf(cpf):
        return "❌ CPF inválido."
    tipo = "morador" if modelo else "visitante"
    veiculos.append({
        "placa": placa.upper(),
        "cpf": cpf,
        "modelo": modelo,
        "tipo": tipo,
        "nome": nome,
        "bloco": bloco,
        "apartamento": apartamento
    })
    return f"✅ Veículo {placa.upper()} cadastrado como {tipo}."

# === Estacionamento ===
def estacionar_veiculo(placa, veiculos, vagas, historico):
    placa = placa.upper()
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
            vaga["entrada"] = datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()
            historico.append({
                "acao": "entrada_veiculo",
                "placa": placa,
                "nome": veiculo["nome"],
                "tipo": veiculo["tipo"],
                "vaga": vaga["numero"],
                "data": vaga["entrada"]
            })
            return f"✅ Veículo {placa} estacionado na vaga {vaga['numero']} ({tipo_vaga})."
    return f"🚫 Nenhuma vaga disponível para tipo {tipo_vaga}."

# === Estacionar por dados (integração com app.py) ===
def estacionar_veiculo_por_dados(cpf, placa, modelo):
    veiculos, vagas, historico, funcionarios = carregar_dados()
    placa = placa.upper()
    veiculo = next((v for v in veiculos if v['cpf'] == cpf and v['placa'] == placa), None)
    if not veiculo:
        return "❌ Veículo com esse CPF e placa não encontrado. Faça o cadastro primeiro."
    resposta = estacionar_veiculo(placa, veiculos, vagas, historico)
    salvar_dados(veiculos, vagas, historico, funcionarios)
    return resposta

# === Liberação de vaga ===
def liberar_vaga(placa, matricula, veiculos, vagas, historico, funcionarios):
    placa = placa.upper()
    vaga = next((v for v in vagas if v["ocupada"] and v["veiculo"] == placa), None)
    veiculo = next((v for v in veiculos if v["placa"] == placa), None)
    funcionario = next((f for f in funcionarios if f["matricula"] == matricula), None)
    if not vaga:
        return "❌ Veículo não encontrado em nenhuma vaga ocupada."
    if not funcionario:
        return "❌ Matrícula de funcionário inválida."
    entrada = datetime.fromisoformat(vaga["entrada"])
    saida = datetime.now(ZoneInfo("America/Sao_Paulo"))
    tempo = (saida - entrada).total_seconds() / 60
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
    return f"✅ Veículo {placa} saiu da vaga {vaga['numero']}. Tempo: {round(tempo)} min."

# === Relatórios ===
def ver_status_vagas(vagas):
    status = ["📋 STATUS DAS VAGAS:"]
    for v in vagas:
        s = "🟢 Livre" if not v["ocupada"] else f"🔴 Ocupada por {v['veiculo']}"
        status.append(f"Vaga {v['numero']} ({v['tipo']}): {s}")
    return "\n".join(status)

def verificar_tempo_excedido(vagas, limite_em_minutos=120):
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    alertas = []
    for vaga in vagas:
        if vaga["ocupada"] and vaga["entrada"]:
            entrada = datetime.fromisoformat(vaga["entrada"])
            tempo = (agora - entrada).total_seconds() / 60
            if tempo > limite_em_minutos:
                alertas.append(f"⚠️ Vaga {vaga['numero']} com veículo {vaga['veiculo']} está há {round(tempo)} min!")
    return "\n".join(alertas) if alertas else "✅ Nenhuma vaga excedeu o tempo."

# === Remoção por CPF ===
def remover_veiculo_por_cpf(cpf, matricula, veiculos, vagas, historico, funcionarios):
    veiculo = next((v for v in veiculos if v["cpf"] == cpf), None)
    funcionario = next((f for f in funcionarios if f["matricula"] == matricula), None)
    if not veiculo:
        return "❌ Nenhum veículo encontrado com este CPF."
    if not funcionario:
        return "❌ Matrícula inválida."
    placa = veiculo["placa"]
    vaga = next((v for v in vagas if v["ocupada"] and v["veiculo"] == placa), None)
    if vaga:
        vaga["ocupada"] = False
        vaga["veiculo"] = None
        vaga["entrada"] = None
    veiculos.remove(veiculo)
    historico.append({
        "acao": "remocao_manual",
        "placa": placa,
        "cpf": cpf,
        "funcionario": funcionario["nome"],
        "matricula": matricula,
        "data": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()
    })
    return f"🗑️ Veículo {placa} removido por {funcionario['nome']}."

# === Funcionários ===
def cadastrar_funcionario(funcionarios, nome, matricula):
    if any(f['matricula'] == matricula for f in funcionarios):
        return "❌ Matrícula já cadastrada."
    funcionarios.append({"nome": nome, "matricula": matricula})
    return f"✅ Funcionário {nome} cadastrado com matrícula {matricula}."

def listar_funcionarios(funcionarios):
    if not funcionarios:
        return "📭 Nenhum funcionário cadastrado."
    return "\n".join([f"Nome: {f['nome']} | Matrícula: {f['matricula']}" for f in funcionarios])

def registrar_entrada(matricula, funcionarios, historico):
    funcionario = next((f for f in funcionarios if f['matricula'] == matricula), None)
    if not funcionario:
        return "❌ Matrícula não encontrada."
    historico.append({
        "acao": "login",
        "matricula": matricula,
        "nome": funcionario['nome'],
        "data": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()
    })
    return f"🔓 Funcionário {funcionario['nome']} entrou."

def registrar_saida(matricula, funcionarios, historico):
    funcionario = next((f for f in funcionarios if f['matricula'] == matricula), None)
    if not funcionario:
        return "❌ Matrícula não encontrada."
    historico.append({
        "acao": "logout",
        "matricula": matricula,
        "nome": funcionario['nome'],
        "data": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()
    })
    return f"🔒 Funcionário {funcionario['nome']} saiu."

# === Listagem de veículos ===
def listar_veiculos_cadastrados(veiculos):
    if not veiculos:
        return "📭 Nenhum veículo cadastrado."
    linhas = ["📄 VEÍCULOS CADASTRADOS:"]
    for v in veiculos:
        linhas.append(
            f"🔹 Placa: {v['placa']} | Nome: {v['nome']} | Tipo: {v['tipo'].capitalize()} | CPF: {v['cpf']} | Modelo: {v.get('modelo', 'N/A')} | Bloco: {v['bloco']} | Apto: {v['apartamento']}"
        )
    return "\n".join(linhas)

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
            menu_supervisor(carregar_dados, salvar_dados, cadastrar_funcionario, listar_funcionarios, listar_veiculos_cadastrados)
        elif opcao == "1":
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
            print(ver_status_vagas(vagas))
        elif opcao == "5":
            print(verificar_tempo_excedido(vagas))
        elif opcao == "6":
            cpf = input("CPF do proprietário: ").strip()
            matricula = input("Matrícula do funcionário: ").strip()
            print(remover_veiculo_por_cpf(cpf, matricula, veiculos, vagas, historico, funcionarios))
        elif opcao == "7":
            nome = input("Nome do funcionário: ").strip()
            matricula = input("Matrícula (4 dígitos): ").strip()
            print(cadastrar_funcionario(funcionarios, nome, matricula))
        elif opcao == "8":
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
