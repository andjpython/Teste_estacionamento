import os
os.environ["PYTHONTZPATH"] = os.path.join(os.path.dirname(__file__), "tzdata")

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from estacionamento import (
    estacionar_veiculo_por_dados,
    remover_veiculo_por_cpf,
    carregar_dados,
    salvar_dados,
    verificar_tempo_excedido,
    cadastrar_veiculo as cadastrar_veiculo_logica,
    cadastrar_funcionario as cadastrar_funcionario_logica,
    listar_funcionarios as listar_funcionarios_logica
)

app = Flask(__name__)
CORS(app)

# Sessão de funcionários logados
funcionarios_logados = set()

# Senha mestre do supervisor
senha_master = "290479"

# ---------------------- ROTAS PRINCIPAIS ----------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login-supervisor', methods=['POST'])
def login_supervisor():
    data = request.get_json()
    senha = data.get('senha')
    if senha == senha_master:
        return jsonify({'mensagem': 'Login do supervisor bem-sucedido!'}), 200
    return jsonify({'mensagem': 'Senha incorreta!'}), 401

@app.route('/cadastrar-veiculo', methods=['POST'])
def cadastrar_veiculo():
    data = request.get_json()
    placa = data.get('placa')
    cpf = data.get('cpf')
    modelo = data.get('modelo', '')
    nome = data.get('nome', '')
    bloco = data.get('bloco', '')
    apartamento = data.get('apartamento', '')

    veiculos, vagas, historico, funcionarios = carregar_dados()
    resposta = cadastrar_veiculo_logica(veiculos, placa, cpf, modelo, nome, bloco, apartamento)
    salvar_dados(veiculos, vagas, historico, funcionarios)

    return jsonify({'mensagem': resposta})

@app.route('/estacionar', methods=['POST'])
def estacionar():
    data = request.get_json()
    placa = data.get('placa')

    from estacionamento import carregar_dados, estacionar_veiculo, salvar_dados
    veiculos, vagas, historico, funcionarios = carregar_dados()

    resposta = estacionar_veiculo(placa, veiculos, vagas, historico)

    salvar_dados(veiculos, vagas, historico, funcionarios)

    return jsonify({'mensagem': resposta})


@app.route('/liberar', methods=['POST'])
def liberar_veiculo():
    data = request.get_json()
    cpf = data.get('cpf')
    matricula = data.get('matricula')

    veiculos, vagas, historico, funcionarios = carregar_dados()

    if matricula not in [f['matricula'] for f in funcionarios]:
        return jsonify({'mensagem': 'Funcionário não cadastrado.'}), 403

    if matricula not in funcionarios_logados:
        return jsonify({'mensagem': 'Funcionário não está logado.'}), 403

    resposta = remover_veiculo_por_cpf(cpf, matricula, veiculos, vagas, historico, funcionarios)
    salvar_dados(veiculos, vagas, historico, funcionarios)

    return jsonify({'mensagem': resposta})

@app.route('/vagas', methods=['GET'])
def listar_vagas():
    veiculos, vagas, historico, funcionarios = carregar_dados()
    return jsonify(vagas)

@app.route('/tempo-excedido', methods=['GET'])
def tempo_excedido():
    veiculos, vagas, historico, funcionarios = carregar_dados()
    alertas = verificar_tempo_excedido(vagas)
    return jsonify({'mensagem': alertas})

@app.route('/cadastrar-funcionario', methods=['POST'])
def cadastrar_funcionario():
    data = request.get_json()
    nome = data.get('nome')
    matricula = data.get('matricula')
    senha = data.get('senha_supervisor')

    if senha != senha_master:
        return jsonify({'mensagem': 'Acesso negado. Senha do supervisor incorreta!'}), 403

    veiculos, vagas, historico, funcionarios = carregar_dados()
    resposta = cadastrar_funcionario_logica(funcionarios, nome, matricula)
    salvar_dados(veiculos, vagas, historico, funcionarios)

    return jsonify({'mensagem': resposta})

@app.route('/funcionarios', methods=['GET'])
def listar_funcionarios():
    senha = request.args.get('senha_supervisor')
    if senha != senha_master:
        return jsonify({'mensagem': 'Acesso negado. Senha incorreta!'}), 403

    veiculos, vagas, historico, funcionarios = carregar_dados()
    return jsonify(funcionarios)

@app.route('/login-funcionario', methods=['POST'])
def login_funcionario():
    data = request.get_json()
    matricula = data.get('matricula')

    veiculos, vagas, historico, funcionarios = carregar_dados()
    if any(f['matricula'] == matricula for f in funcionarios):
        funcionarios_logados.add(matricula)
        return jsonify({'mensagem': f'Funcionário {matricula} logado com sucesso!'}), 200

    return jsonify({'mensagem': 'Matrícula não encontrada!'}), 404

@app.route('/logout-funcionario', methods=['POST'])
def logout_funcionario():
    data = request.get_json()
    matricula = data.get('matricula')

    if matricula in funcionarios_logados:
        funcionarios_logados.remove(matricula)
        return jsonify({'mensagem': f'Funcionário {matricula} deslogado com sucesso!'}), 200

    return jsonify({'mensagem': 'Funcionário não estava logado.'}), 400

# ---------------------- EXECUÇÃO ----------------------
if __name__ == '__main__':
    app.run(debug=True)
