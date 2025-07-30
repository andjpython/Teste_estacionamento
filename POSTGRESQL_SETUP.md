# 🐘 Configuração PostgreSQL para Sistema de Estacionamento

## 📋 Pré-requisitos

### Instalar PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**CentOS/RHEL:**
```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
```

**macOS (com Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
- Baixe do site oficial: https://www.postgresql.org/download/windows/

## 🔧 Configuração Inicial

### 1. Acessar PostgreSQL
```bash
sudo -u postgres psql
```

### 2. Criar Banco de Dados
```sql
-- Criar usuário para o sistema
CREATE USER estacionamento_user WITH ENCRYPTED PASSWORD 'sua_senha_segura';

-- Criar banco de dados
CREATE DATABASE estacionamento_db OWNER estacionamento_user;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE estacionamento_db TO estacionamento_user;

-- Sair do psql
\q
```

### 3. Testar Conexão
```bash
psql -h localhost -U estacionamento_user -d estacionamento_db
```

## 🌐 Configurações de Ambiente

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# Configuração PostgreSQL
DATABASE_URL=postgresql://estacionamento_user:sua_senha_segura@localhost:5432/estacionamento_db

# Configuração Flask
FLASK_ENV=production
SENHA_SUPERVISOR=290479

# Configurações opcionais
SQLALCHEMY_ECHO=False
```

### Para Desenvolvimento Local
```bash
export DATABASE_URL="postgresql://estacionamento_user:sua_senha_segura@localhost:5432/estacionamento_db"
```

### Para Produção (Heroku/Render)
```bash
# A variável DATABASE_URL é automaticamente configurada pelo provedor
# Apenas certifique-se de que está usando PostgreSQL no plano
```

## 🔐 Configuração de Segurança

### 1. Arquivo pg_hba.conf
Localização comum: `/etc/postgresql/*/main/pg_hba.conf`

Adicionar/modificar linha para conexões locais:
```
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
```

### 2. Arquivo postgresql.conf
Localização comum: `/etc/postgresql/*/main/postgresql.conf`

Configurações recomendadas:
```
listen_addresses = 'localhost'
port = 5432
max_connections = 100
shared_buffers = 128MB
```

### 3. Reiniciar PostgreSQL
```bash
sudo systemctl restart postgresql
```

## 📊 URLs de Conexão por Ambiente

### Desenvolvimento Local
```
postgresql://username:password@localhost:5432/estacionamento_db
```

### Docker
```
postgresql://username:password@postgres:5432/estacionamento_db
```

### Heroku
```
# Automático via DATABASE_URL
postgres://user:pass@host:5432/dbname
```

### Render
```
# Automático via DATABASE_URL
postgresql://user:pass@host:5432/dbname
```

### Supabase
```
postgresql://postgres:password@db.host.supabase.co:5432/postgres
```

## 🚀 Executar Migração

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variável de Ambiente
```bash
export DATABASE_URL="postgresql://estacionamento_user:sua_senha_segura@localhost:5432/estacionamento_db"
```

### 3. Executar Script de Migração
```bash
python migrate_to_postgresql.py
```

### 4. Iniciar Aplicação
```bash
python app.py
```

## 🔍 Verificação e Troubleshooting

### Verificar Status do PostgreSQL
```bash
sudo systemctl status postgresql
```

### Verificar Logs
```bash
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Testar Conexão Python
```python
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="estacionamento_db",
        user="estacionamento_user",
        password="sua_senha_segura"
    )
    print("✅ Conexão bem-sucedida!")
    conn.close()
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
```

### Comandos Úteis do psql
```sql
-- Listar bancos de dados
\l

-- Conectar a um banco
\c estacionamento_db

-- Listar tabelas
\dt

-- Descrever tabela
\d nome_da_tabela

-- Verificar dados
SELECT COUNT(*) FROM veiculos;
SELECT COUNT(*) FROM vagas;
SELECT COUNT(*) FROM funcionarios;
SELECT COUNT(*) FROM historico;
```

## 🐳 Docker (Opcional)

### docker-compose.yml
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: estacionamento_db
      POSTGRES_USER: estacionamento_user
      POSTGRES_PASSWORD: sua_senha_segura
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://estacionamento_user:sua_senha_segura@postgres:5432/estacionamento_db
    depends_on:
      - postgres

volumes:
  postgres_data:
```

### Executar com Docker
```bash
docker-compose up -d
```

## ⚡ Performance e Otimização

### Índices Recomendados
```sql
-- Já criados automaticamente pelos modelos SQLAlchemy
CREATE INDEX IF NOT EXISTS idx_veiculos_placa ON veiculos(placa);
CREATE INDEX IF NOT EXISTS idx_vagas_numero ON vagas(numero);
CREATE INDEX IF NOT EXISTS idx_funcionarios_matricula ON funcionarios(matricula);
CREATE INDEX IF NOT EXISTS idx_historico_data ON historico(data_operacao);
CREATE INDEX IF NOT EXISTS idx_historico_placa ON historico(placa_veiculo);
```

### Configurações de Performance
```sql
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

## 🔄 Backup e Restore

### Criar Backup
```bash
pg_dump -h localhost -U estacionamento_user estacionamento_db > backup.sql
```

### Restaurar Backup
```bash
psql -h localhost -U estacionamento_user estacionamento_db < backup.sql
```

### Backup Automático (Crontab)
```bash
# Adicionar ao crontab
0 2 * * * pg_dump -h localhost -U estacionamento_user estacionamento_db > /backups/estacionamento_$(date +\%Y\%m\%d).sql
```

## 📞 Suporte

Em caso de problemas:
1. Verifique os logs do PostgreSQL
2. Confirme as configurações de conexão
3. Teste a conexão manualmente
4. Verifique permissões do usuário
5. Consulte a documentação oficial: https://www.postgresql.org/docs/