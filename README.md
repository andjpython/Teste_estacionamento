# 🅿️ Sistema de Estacionamento Rotativo para Condomínios

Projeto desenvolvido em Python com Flask para automatizar o controle de vagas rotativas em condomínios. A aplicação permite cadastro e gerenciamento de veículos (moradores e visitantes), controle de tempo de permanência, autenticação de funcionários e visualização em tempo real via interface web.

---

## 🚀 Funcionalidades

- Cadastro de veículos (morador ou visitante)
- Estacionamento com validação de CPF e placa
- Liberação de veículos com matrícula do funcionário
- Alerta de tempo excedido (ex: mais de 72h)
- Histórico completo de entradas e saídas
- Interface web (HTML + CSS + JS)
- Área exclusiva para o supervisor com login e ações administrativas

---

## 🧰 Tecnologias Utilizadas

- Python 3.10+
- Flask
- HTML5 e CSS3
- JavaScript (fetch API)
- JSON para persistência de dados

---

## 🖥️ Estrutura do Projeto

```
📁 Estacionamento_Rotativo
├── app.py              # Backend Flask com rotas da API
├── estacionamento.py   # Lógica principal de negócio
├── supervisor.py       # Funcionalidades de supervisão
├── index.html          # Interface do sistema
├── style.css           # Estilo da interface
├── dados/              # Dados salvos em JSON
│   ├── vagas.json
│   ├── veiculos.json
│   ├── historico.json
│   └── funcionarios.json
```

---

## 🔐 Supervisor

Acesso ao painel do supervisor (terminal):

- **Senha padrão:** `2904`
- Ações disponíveis:
  - Cadastrar/remover funcionários
  - Ver histórico completo
  - Listar veículos cadastrados

---

## 📸 Captura de Tela

![screenshot](imagens/tela-sistema.png)

---

## 📦 Como executar o projeto

1. Clone o repositório:
```bash
git clone https://github.com/ejpython/Estacionamento_Rotativo.git
```

2. Acesse a pasta:
```bash
cd Estacionamento_Rotativo
```

3. Instale as dependências:
```bash
pip install flask flask-cors
```

4. Execute o sistema:
```bash
python app.py
```

5. Abra no navegador:
```
http://127.0.0.1:5000/
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se à vontade para usar, estudar, adaptar e compartilhar.

---

## ✍️ Autor

Anderson Jacinto da Silveira  
Aluno de Engenharia de Software – UNIASSELVI  
GitHub: [@ejpython](https://github.com/ejpython)

---