#!/usr/bin/env python3
"""
Script de Migração: JSON → PostgreSQL
Sistema de Estacionamento Rotativo

Este script migra os dados existentes dos arquivos JSON para o banco PostgreSQL.
Executa uma migração segura com backup e validação.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

from flask import Flask
from config import active_config
from models import db, Veiculo, Vaga, Funcionario, Historico
from models.database import init_db

def criar_app():
    """Cria a aplicação Flask para migração"""
    app = Flask(__name__)
    
    # Configurar SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = active_config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = active_config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = active_config.SQLALCHEMY_ENGINE_OPTIONS
    
    # Inicializar base de dados
    init_db(app)
    
    return app

def carregar_json(arquivo_path):
    """Carrega dados de um arquivo JSON"""
    try:
        if arquivo_path.exists():
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar {arquivo_path}: {e}")
        return []

def migrar_veiculos(app):
    """Migra veículos do JSON para PostgreSQL"""
    print("\n🚗 Migrando veículos...")
    
    with app.app_context():
        dados_veiculos = carregar_json(active_config.VEICULOS_PATH)
        
        total = len(dados_veiculos)
        migrados = 0
        
        for veiculo_data in dados_veiculos:
            try:
                # Verificar se já existe
                veiculo_existente = Veiculo.buscar_por_placa(veiculo_data['placa'])
                if veiculo_existente:
                    print(f"  ⚠️  Veículo {veiculo_data['placa']} já existe - ignorando")
                    continue
                
                # Criar novo veículo
                veiculo = Veiculo.from_dict(veiculo_data)
                veiculo.salvar()
                migrados += 1
                print(f"  ✅ Veículo {veiculo.placa} migrado")
                
            except Exception as e:
                print(f"  ❌ Erro ao migrar veículo {veiculo_data.get('placa', 'N/A')}: {e}")
        
        print(f"📊 Veículos: {migrados}/{total} migrados com sucesso")
        return migrados

def migrar_funcionarios(app):
    """Migra funcionários do JSON para PostgreSQL"""
    print("\n👨‍💼 Migrando funcionários...")
    
    with app.app_context():
        dados_funcionarios = carregar_json(active_config.FUNCIONARIOS_PATH)
        
        total = len(dados_funcionarios)
        migrados = 0
        
        for funcionario_data in dados_funcionarios:
            try:
                # Verificar se já existe
                funcionario_existente = Funcionario.buscar_por_matricula(funcionario_data['matricula'])
                if funcionario_existente:
                    print(f"  ⚠️  Funcionário {funcionario_data['matricula']} já existe - ignorando")
                    continue
                
                # Criar novo funcionário
                funcionario = Funcionario.from_dict(funcionario_data)
                funcionario.salvar()
                migrados += 1
                print(f"  ✅ Funcionário {funcionario.nome} ({funcionario.matricula}) migrado")
                
            except Exception as e:
                print(f"  ❌ Erro ao migrar funcionário {funcionario_data.get('matricula', 'N/A')}: {e}")
        
        print(f"📊 Funcionários: {migrados}/{total} migrados com sucesso")
        return migrados

def migrar_vagas(app):
    """Migra vagas do JSON para PostgreSQL"""
    print("\n🅿️  Migrando vagas...")
    
    with app.app_context():
        dados_vagas = carregar_json(active_config.VAGAS_PATH)
        
        total = len(dados_vagas)
        migrados = 0
        
        for vaga_data in dados_vagas:
            try:
                # Verificar se já existe
                vaga_existente = Vaga.buscar_por_numero(vaga_data['numero'])
                if vaga_existente:
                    # Atualizar estado da vaga existente
                    vaga_existente.ocupada = vaga_data['ocupada']
                    vaga_existente.placa_veiculo = vaga_data.get('veiculo')
                    
                    if vaga_data.get('entrada'):
                        try:
                            if isinstance(vaga_data['entrada'], str):
                                vaga_existente.entrada = datetime.fromisoformat(vaga_data['entrada'].replace('Z', '+00:00'))
                            else:
                                vaga_existente.entrada = vaga_data['entrada']
                        except:
                            vaga_existente.entrada = None
                    
                    db.session.commit()
                    print(f"  🔄 Vaga {vaga_data['numero']} atualizada")
                    migrados += 1
                    continue
                
                # Criar nova vaga
                vaga = Vaga.from_dict(vaga_data)
                vaga.salvar()
                migrados += 1
                print(f"  ✅ Vaga {vaga.numero} ({vaga.tipo}) migrada")
                
            except Exception as e:
                print(f"  ❌ Erro ao migrar vaga {vaga_data.get('numero', 'N/A')}: {e}")
        
        print(f"📊 Vagas: {migrados}/{total} migradas com sucesso")
        return migrados

def migrar_historico(app):
    """Migra histórico do JSON para PostgreSQL"""
    print("\n📊 Migrando histórico...")
    
    with app.app_context():
        dados_historico = carregar_json(active_config.HISTORICO_PATH)
        
        total = len(dados_historico)
        migrados = 0
        
        for historico_data in dados_historico:
            try:
                # Criar novo registro de histórico
                historico = Historico.from_dict(historico_data)
                historico.salvar()
                migrados += 1
                
                if migrados % 50 == 0:  # Log a cada 50 registros
                    print(f"  📈 {migrados}/{total} registros de histórico migrados...")
                
            except Exception as e:
                print(f"  ❌ Erro ao migrar registro de histórico: {e}")
        
        print(f"📊 Histórico: {migrados}/{total} registros migrados com sucesso")
        return migrados

def fazer_backup_json():
    """Cria backup dos arquivos JSON antes da migração"""
    print("\n💾 Criando backup dos arquivos JSON...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backup_json_{timestamp}")
    backup_dir.mkdir(exist_ok=True)
    
    arquivos_json = [
        active_config.VEICULOS_PATH,
        active_config.VAGAS_PATH,
        active_config.FUNCIONARIOS_PATH,
        active_config.HISTORICO_PATH
    ]
    
    for arquivo in arquivos_json:
        if arquivo.exists():
            backup_path = backup_dir / arquivo.name
            import shutil
            shutil.copy2(arquivo, backup_path)
            print(f"  ✅ Backup criado: {backup_path}")
    
    print(f"📁 Backup completo em: {backup_dir}")
    return backup_dir

def verificar_conexao_db(app):
    """Verifica se a conexão com PostgreSQL está funcionando"""
    print("\n🔌 Verificando conexão com PostgreSQL...")
    
    with app.app_context():
        try:
            # Tentar conectar e fazer uma query simples
            result = db.session.execute(db.text('SELECT 1')).fetchone()
            if result:
                print("  ✅ Conexão com PostgreSQL estabelecida com sucesso")
                return True
        except Exception as e:
            print(f"  ❌ Erro de conexão com PostgreSQL: {e}")
            print("\n💡 Verifique:")
            print("  - Se o PostgreSQL está rodando")
            print("  - Se a DATABASE_URL está correta")
            print("  - Se o banco de dados existe")
            return False

def main():
    """Função principal de migração"""
    print("🚀 Iniciando Migração: JSON → PostgreSQL")
    print("=" * 50)
    
    # Verificar se os arquivos JSON existem
    arquivos_necessarios = [
        active_config.VEICULOS_PATH,
        active_config.VAGAS_PATH,
        active_config.FUNCIONARIOS_PATH,
        active_config.HISTORICO_PATH
    ]
    
    arquivos_existentes = [arq for arq in arquivos_necessarios if arq.exists()]
    
    if not arquivos_existentes:
        print("❌ Nenhum arquivo JSON encontrado para migrar!")
        return
    
    print(f"📁 Arquivos encontrados: {len(arquivos_existentes)}/{len(arquivos_necessarios)}")
    
    # Criar aplicação Flask
    app = criar_app()
    
    # Verificar conexão
    if not verificar_conexao_db(app):
        return
    
    # Fazer backup
    backup_dir = fazer_backup_json()
    
    # Executar migrações
    total_migrados = 0
    
    try:
        total_migrados += migrar_funcionarios(app)
        total_migrados += migrar_veiculos(app)
        total_migrados += migrar_vagas(app)
        total_migrados += migrar_historico(app)
        
        print("\n" + "=" * 50)
        print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📊 Total de registros migrados: {total_migrados}")
        print(f"💾 Backup salvo em: {backup_dir}")
        
        # Estatísticas finais
        with app.app_context():
            print("\n📈 Estatísticas do banco PostgreSQL:")
            print(f"  - Veículos: {Veiculo.query.count()}")
            print(f"  - Funcionários: {Funcionario.contar_ativos()}")
            print(f"  - Vagas: {Vaga.query.count()}")
            print(f"  - Histórico: {Historico.query.count()}")
        
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        print(f"💾 Dados de backup disponíveis em: {backup_dir}")

if __name__ == "__main__":
    # Verificar se o usuário quer prosseguir
    print("⚠️  Este script irá migrar seus dados JSON para PostgreSQL.")
    print("Um backup será criado automaticamente.")
    
    resposta = input("\nDeseja continuar? (s/N): ").lower().strip()
    if resposta in ['s', 'sim', 'y', 'yes']:
        main()
    else:
        print("❌ Migração cancelada pelo usuário.")