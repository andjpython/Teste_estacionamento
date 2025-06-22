import json
from datetime import datetime
from zoneinfo import ZoneInfo
from getpass import getpass

def ver_historico(historico):
    if not historico:
        return "📭 Nenhum registro no histórico."
    return "\n".join([
        f"{h.get('data', h.get('data_saida', ''))}: {h['acao']} - {h.get('placa', '')} - {h.get('nome', '')}"
        for h in historico
    ])

def remover_funcionario(funcionarios, matricula):
    func = next((f for f in funcionarios if f["matricula"] == matricula), None)
    if not func:
        return "❌ Funcionário não encontrado."
    funcionarios.remove(func)
    return f"🗑️ Funcionário {func['nome']} removido."

def menu_supervisor(carregar_dados, salvar_dados, cadastrar_funcionario, listar_funcionarios, listar_veiculos_cadastrados):
    senha = getpass("Digite a senha de supervisor: ")
    if senha != "2904":
        print("❌ Senha incorreta!")
        return

    veiculos, vagas, historico, funcionarios = carregar_dados()

    while True:
        print("\n==== MENU DO SUPERVISOR ====")
        print("1. Cadastrar funcionário")
        print("2. Listar funcionários")
        print("3. Ver histórico completo")
        print("4. Remover funcionário")
        print("5. Listar veículos cadastrados")
        print("6. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            nome = input("Nome do funcionário: ").strip()
            matricula = input("Matrícula (4 dígitos): ").strip()
            print(cadastrar_funcionario(funcionarios, nome, matricula))
        elif opcao == "2":
            print(listar_funcionarios(funcionarios))
        elif opcao == "3":
            print(ver_historico(historico))
        elif opcao == "4":
            matricula = input("Matrícula do funcionário a remover: ").strip()
            print(remover_funcionario(funcionarios, matricula))
        elif opcao == "5":
            print(listar_veiculos_cadastrados(veiculos))
        elif opcao == "6":
            print("🔙 Retornando ao menu principal...")
            break
        else:
            print("❌ Opção inválida!")

        salvar_dados(veiculos, vagas, historico, funcionarios)
