# 🅿️ Sistema de Estacionamento Rotativo - Recantos das Flores I

Sistema profissional para gestão de estacionamento rotativo em condomínios, desenvolvido com Python (Flask), HTML5, CSS3 e JavaScript. Arquitetura modular, responsiva e segura, seguindo boas práticas de desenvolvimento.

---

## ✨ Funcionalidades Principais

### 🔐 **Controle de Acesso**
- Login/logout de funcionários com controle de sessão
- Área restrita do supervisor com senha configurável
- Auditoria completa de todas as operações

### 🚗 **Gestão de Veículos**
- Cadastro com validação de CPF e placas (antigo/Mercosul)
- Suporte a moradores e visitantes
- Sistema de tipos automático baseado no modelo

### 🅿️ **Controle de Vagas**
- 20 vagas comuns (moradores) + 10 visitantes
- Timer regressivo em tempo real (10 minutos limite)
- Alertas visuais por cores (verde/amarelo/vermelho)
- Auto-refresh e cleanup de memória

### 📊 **Relatórios e Histórico**
- Histórico completo de operações
- Relatórios de tempo excedido
- Listagem de veículos e funcionários
- Logs estruturados para auditoria

### 🎨 **Interface Moderna**
- Design responsivo (mobile-first)
- Layout institucional profissional
- Animações CSS suaves
- Feedback imediato de operações

---

## 🏗️ Arquitetura Refatorada (v2.1.0)

### Estrutura Modular

```
📁 estacionamento_rotativo1
├── app.py                # Backend Flask (registra blueprints)
├── estacionamento.py     # Lógica principal de negócio
├── supervisor.py         # Funções de supervisão (terminal)
├── routes/               # Blueprints Flask (rotas)
│   ├── supervisor_routes.py
│   ├── funcionarios_routes.py
│   └── veiculos_routes.py
├── services/             # Lógica de negócio modularizada
│   ├── veiculo_service.py
│   ├── funcionario_service.py
│   ├── vaga_service.py
│   └── historico_service.py
├── models/               # (Reservado para modelos de dados)
├── dados/                # Dados persistentes em JSON
│   ├── vagas.json
│   ├── veiculos.json
│   ├── historico.json
│   └── funcionarios.json
├── static/
│   ├── style.css         # Estilo institucional e responsivo
│   ├── script.js         # JS moderno e integrado
│   └── imagens/          # Logos, fotos, imagens flutuantes
├── templates/
│   └── index.html        # Layout institucional e profissional
└── README.md
```

---

## 📸 Capturas de Tela

> **Adicione prints do sistema rodando aqui!**

---

## 📦 Como executar o projeto

### 🐘 Versão PostgreSQL (Recomendada)

1. **Clone o repositório:**
```bash
git clone <URL_DO_REPOSITORIO>
cd estacionamento_rotativo1
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure PostgreSQL:**
   - Siga o guia detalhado: [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)
   - Ou use o comando rápido:
   ```bash
   # Instalar PostgreSQL (Ubuntu/Debian)
   sudo apt update && sudo apt install postgresql postgresql-contrib
   
   # Criar banco e usuário
   sudo -u postgres psql -c "CREATE USER estacionamento_user WITH ENCRYPTED PASSWORD 'sua_senha_segura';"
   sudo -u postgres psql -c "CREATE DATABASE estacionamento_db OWNER estacionamento_user;"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE estacionamento_db TO estacionamento_user;"
   ```

4. **Configure as variáveis de ambiente:**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite as configurações (especialmente DATABASE_URL)
nano .env
```

5. **Execute a migração dos dados (se houver dados JSON):**
```bash
python migrate_to_postgresql.py
```

6. **Execute o sistema:**
```bash
python app.py
```

7. **Acesse no navegador:**
```
http://127.0.0.1:5000/
```

### 📁 Versão JSON (Legacy)

Para usar a versão anterior com arquivos JSON:

1. **Clone e instale:**
```bash
git clone <URL_DO_REPOSITORIO>
cd estacionamento_rotativo1
pip install flask flask-cors pytz
```

2. **Configure variáveis (opcional):**
```bash
export SENHA_SUPERVISOR=suasenha
```

3. **Execute:**
```bash
python app.py
```

---

## 🔐 Supervisor
- Acesso ao painel do supervisor (terminal ou web)
- Senha padrão: `290479` (ou variável de ambiente)
- Ações: cadastrar/remover funcionários, ver histórico, listar veículos

---

## 📋 Documentação

- **README.md**: Documentação principal do projeto
- **CHANGELOG.md**: Histórico de mudanças e versões
- **requirements.txt**: Dependências do projeto

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se à vontade para usar, estudar, adaptar e compartilhar.

---

## 🗄️ Banco de Dados PostgreSQL

### Vantagens da Migração

✅ **Desempenho Superior:** Consultas otimizadas e índices automáticos  
✅ **Concorrência:** Múltiplos usuários simultâneos sem conflitos  
✅ **Integridade:** Relacionamentos e validações no banco  
✅ **Escalabilidade:** Suporte a milhares de registros  
✅ **Backup Automático:** Ferramentas nativas de backup/restore  
✅ **Deploy Facilitado:** Compatível com Heroku, Render, Railway, etc.

### Estrutura do Banco

```sql
-- Tabelas criadas automaticamente
veiculos (id, placa, nome, cpf, modelo, tipo, bloco, apartamento, data_cadastro)
vagas (id, numero, tipo, ocupada, placa_veiculo, entrada)
funcionarios (id, nome, matricula, cargo, data_cadastro, ativo)
historico (id, tipo_operacao, placa_veiculo, numero_vaga, funcionario_matricula, 
          funcionario_nome, tempo_permanencia, observacoes, data_operacao)
```

### Recursos Avançados

- **Relacionamentos:** Foreign keys entre veículos e vagas
- **Índices:** Busca otimizada por placa, matrícula, data
- **Soft Delete:** Funcionários desativados em vez de removidos
- **Auditoria Completa:** Histórico detalhado de todas as operações
- **Timezone:** Suporte nativo a fusos horários
- **Validações:** Constraints no banco de dados

---

## ✍️ Autor

Anderson Jacinto da Silveira  
Aluno de Engenharia de Software – UNIASSELVI