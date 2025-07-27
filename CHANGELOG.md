# Changelog - Sistema de Estacionamento Rotativo

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2025-01-29 - CORREÇÕES CRÍTICAS DE BUGS

### 🐛 **BUGS CORRIGIDOS**

#### **Críticos**
- ✅ **Codificação UTF-8**: Corrigidos caracteres corrompidos nos nomes dos funcionários (JoÃ£o → João, ConceiÃ§Ã£o → Conceição)
- ✅ **Duplicação de rotas**: Removidas rotas duplicadas entre `app.py` e blueprints, evitando conflitos
- ✅ **Validação de CPF**: Implementada validação completa com algoritmo de dígitos verificadores
- ✅ **Normalização de dados**: CPFs padronizados (apenas números) e placas normalizadas (maiúsculas, sem espaços)
- ✅ **Controle de sessão**: Corrigida inconsistência entre frontend (localStorage) e backend (set)
- ✅ **Salvamento duplo**: Otimizado para salvar dados apenas uma vez por operação

#### **Funcionais**
- ✅ **Tratamento de erros**: Implementado logging detalhado em todos os serviços
- ✅ **Validação de placa**: Suporte robusto para formatos antigo (ABC1234) e Mercosul (ABC1D23)
- ✅ **Verificação de login**: Funcionários agora precisam estar logados para todas as operações
- ✅ **Normalização de entrada**: Dados de entrada são sanitizados e validados consistentemente
- ✅ **Codificação de arquivos**: Todos os arquivos JSON agora usam UTF-8 explicitamente

### 📈 **MELHORIAS**

#### **Segurança**
- ✅ Validação de entrada de dados em todas as rotas
- ✅ Verificação obrigatória de login para operações críticas
- ✅ Tratamento seguro de erros sem exposição de dados internos

#### **Performance**
- ✅ Eliminado salvamento duplo de dados (redução de ~50% das operações I/O)
- ✅ Otimizada normalização de dados com funções dedicadas
- ✅ Implementado logging configurável para debug e monitoramento

#### **Manutenibilidade**
- ✅ Código refatorado com funções de normalização centralizadas
- ✅ Logging estruturado para facilitar debugging
- ✅ Separação clara de responsabilidades entre rotas e serviços
- ✅ Validações consistentes em toda a aplicação

#### **Usabilidade**
- ✅ Mensagens de erro mais claras e específicas
- ✅ Validação de dados antes do processamento
- ✅ Feedback detalhado sobre operações realizadas

### 🔧 **ARQUITETURA**

#### **Estrutura Otimizada**
```
app.py                    # Apenas rotas principais e configuração
├── routes/              # Rotas específicas por domínio
│   ├── funcionarios_routes.py  # Login/logout, cadastro
│   ├── veiculos_routes.py      # CRUD veículos, estacionamento
│   └── supervisor_routes.py    # Área do supervisor
├── services/            # Lógica de negócio
│   ├── funcionario_service.py # Validações e operações
│   ├── veiculo_service.py     # Normalização e cadastro
│   └── vaga_service.py        # Status e tempo excedido
└── dados/              # Dados normalizados UTF-8
    ├── funcionarios.json
    ├── veiculos.json
    ├── vagas.json
    └── historico.json
```

### 📋 **VALIDAÇÕES IMPLEMENTADAS**

#### **CPF**
- ✅ Algoritmo completo de validação de dígitos verificadores
- ✅ Normalização automática (remove pontuação)
- ✅ Verificação de CPFs inválidos comuns (111.111.111-11, etc.)

#### **Placa**
- ✅ Suporte aos formatos: ABC1234 (antigo) e ABC1D23 (Mercosul)
- ✅ Normalização automática (maiúsculas, sem espaços)
- ✅ Validação por regex robusta

#### **Sessão**
- ✅ Controle centralizado de funcionários logados
- ✅ Verificação obrigatória para operações críticas
- ✅ Registro de login/logout no histórico

### 🚨 **BREAKING CHANGES**

- **Rotas**: Algumas rotas foram movidas para blueprints específicos
- **Dados**: CPFs normalizados podem afetar buscas antigas
- **Sessão**: Login obrigatório para todas as operações

### 🔬 **TESTES REALIZADOS**

- ✅ Importação de módulos sem erros
- ✅ Validação de CPF com casos extremos
- ✅ Normalização de placas e dados
- ✅ Controle de sessão de funcionários
- ✅ Operações CRUD completas
- ✅ Tratamento de erros e logging

---

## [1.0.0] - 2025-01-25 - Versão Inicial

### ✨ **FUNCIONALIDADES**
- Sistema de estacionamento rotativo
- Cadastro de veículos e funcionários
- Controle de vagas (comum/visitante)
- Histórico de operações
- Interface web responsiva
- Área do supervisor

### 🐛 **PROBLEMAS CONHECIDOS** (Corrigidos em v2.0.0)
- Codificação de caracteres especiais
- Validação de CPF limitada
- Duplicação de rotas
- Controle de sessão inconsistente
- Salvamento duplo de dados

---

## Notas de Desenvolvimento

### Estrutura do Projeto
```
📁 estacionamento_rotativo1
├── app.py                # Aplicação principal Flask
├── estacionamento.py     # Lógica de negócio
├── routes/               # Blueprints Flask
├── services/             # Serviços de negócio
├── static/               # Assets estáticos (CSS, JS, imagens)
├── templates/            # Templates HTML
├── dados/                # Dados persistentes JSON
└── README.md             # Documentação principal
```

### Funcionalidades Principais
- **Gestão de Veículos**: Cadastro, estacionamento, saída
- **Controle de Vagas**: Monitoramento de tempo e notificações
- **Autenticação**: Login/logout para funcionários e supervisor
- **Interface**: Design responsivo e moderno
- **Navegação**: Botões "Voltar" em todas as seções

### Tecnologias Utilizadas
- Python 3.10+
- Flask (Framework web)
- HTML5, CSS3, JavaScript
- JSON (Persistência de dados)

---

**Desenvolvido por**: Anderson Jacinto da Silveira  
**Projeto**: Sistema de Estacionamento Rotativo - Recantos das Flores I 