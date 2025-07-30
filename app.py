import os
import pytz
from datetime import datetime

from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from config import active_config

# Importar modelos e configuração da base de dados
from models import db, Veiculo, Vaga, Funcionario, Historico
from models.database import init_db

# Importar rotas
from routes.supervisor_routes import supervisor_bp
from routes.funcionarios_routes import funcionarios_bp
from routes.veiculos_routes import veiculos_bp

app = Flask(__name__)
CORS(app)

# Configurar SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = active_config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = active_config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = active_config.SQLALCHEMY_ENGINE_OPTIONS

# Inicializar base de dados
init_db(app)

app.register_blueprint(supervisor_bp)
app.register_blueprint(funcionarios_bp)
app.register_blueprint(veiculos_bp)

# ---------------------- ROTAS PRINCIPAIS ----------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sistema')
def sistema():
    return render_template('sistema.html')

@app.route('/supervisor')
def supervisor_area():
    return render_template('supervisor.html', nome_supervisor='Anderson J Silveira')

@app.route('/supervisor-sistema')
def supervisor_sistema():
    return render_template('supervisor_sistema.html', nome_supervisor='Anderson J Silveira')



@app.route('/vagas-completas', methods=['GET'])
def listar_vagas_completas():
    try:
        # Buscar todas as vagas com informações dos veículos
        vagas = Vaga.query.all()
        vagas_completas = []
        
        for vaga in vagas:
            vaga_info = vaga.to_dict()
            if vaga.ocupada and vaga.veiculo_estacionado:
                veiculo = vaga.veiculo_estacionado
                vaga_info.update({
                    'proprietario': veiculo.nome,
                    'cpf': veiculo.cpf,
                    'modelo': veiculo.modelo,
                    'bloco': veiculo.bloco,
                    'apartamento': veiculo.apartamento
                })
            
            vagas_completas.append(vaga_info)
        
        return jsonify(vagas_completas)
    except Exception as e:
        print(f"Erro ao carregar vagas completas: {str(e)}")
        return jsonify({'mensagem': f'Erro ao carregar vagas completas: {str(e)}'}), 500

# ---------------------- EXECUÇÃO ----------------------
if __name__ == '__main__':
    # Configuração para produção no Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
