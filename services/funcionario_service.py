# === Cadastro de funcionário ===
def cadastrar_funcionario(funcionarios, nome, matricula):
    if any(f['matricula'] == matricula for f in funcionarios):
        return "❌ Matrícula já cadastrada."
    if not matricula or len(matricula) != 4 or not matricula.isdigit():
        return "❌ Matrícula inválida. Deve conter 4 dígitos."
    if not nome:
        return "❌ Nome do funcionário é obrigatório."
    funcionarios.append({
        "nome": nome,
        "matricula": matricula
    })
    return f"✅ Funcionário {nome} cadastrado com matrícula {matricula}."

# === Listar funcionários ===
def listar_funcionarios(funcionarios):
    if not funcionarios:
        return "📭 Nenhum funcionário cadastrado."
    return "\n".join([f"Nome: {f['nome']} | Matrícula: {f['matricula']}" for f in funcionarios])

# === Buscar funcionário por matrícula ===
def buscar_funcionario_por_matricula(funcionarios, matricula):
    return next((f for f in funcionarios if f['matricula'] == matricula), None) 