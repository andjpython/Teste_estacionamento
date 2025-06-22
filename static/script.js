// ✅ Login do Supervisor
document.getElementById('formLoginSupervisor').addEventListener('submit', async function (e) {
  e.preventDefault();
  const senha = this.senha.value;

  const res = await fetch('/login-supervisor', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ senha })
  });

  const dados = await res.json();
  document.getElementById('mensagemSupervisor').innerText = dados.mensagem;
});

// ✅ Cadastrar Funcionário
document.getElementById('formCadastroFuncionario').addEventListener('submit', async function (e) {
  e.preventDefault();
  const nome = this.nome.value;
  const matricula = this.matricula.value;
  const senha_supervisor = this.senha_supervisor.value;

  const res = await fetch('/cadastrar-funcionario', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome, matricula, senha_supervisor })
  });

  const dados = await res.json();
  document.getElementById('mensagemCadastroFuncionario').innerText = dados.mensagem;
});

// ✅ Listar Funcionários
async function listarFuncionarios() {
  const senha = document.getElementById('senhaListar').value;

  const res = await fetch(`/funcionarios?senha_supervisor=${senha}`);
  const lista = document.getElementById('listaFuncionarios');
  lista.innerHTML = '';

  const dados = await res.json();

  if (dados.mensagem) {
    lista.innerHTML = `<li>${dados.mensagem}</li>`;
  } else {
    for (const funcionario of dados) {
      const li = document.createElement('li');
      li.textContent = `${funcionario.nome} (Matrícula: ${funcionario.matricula})`;
      lista.appendChild(li);
    }
  }
}

// ✅ Login Funcionário
document.getElementById('formLoginFuncionario').addEventListener('submit', async function (e) {
  e.preventDefault();
  const matricula = this.matricula.value;

  const res = await fetch('/login-funcionario', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ matricula })
  });

  const dados = await res.json();
  document.getElementById('mensagemLoginFuncionario').innerText = dados.mensagem;
});

// ✅ Logout Funcionário
document.getElementById('formLogoutFuncionario').addEventListener('submit', async function (e) {
  e.preventDefault();
  const matricula = this.matricula.value;

  const res = await fetch('/logout-funcionario', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ matricula })
  });

  const dados = await res.json();
  document.getElementById('mensagemLogoutFuncionario').innerText = dados.mensagem;
});

// ✅ Cadastrar Veículo
document.getElementById('formCadastrarVeiculo').addEventListener('submit', async function (e) {
  e.preventDefault();
  const cpf = this.cpf.value;
  const placa = this.placa.value;
  const modelo = this.modelo.value;
  const nome = this.nome.value;
  const bloco = this.bloco.value;
  const apartamento = this.apartamento.value;

  const res = await fetch('/cadastrar-veiculo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cpf, placa, modelo, nome, bloco, apartamento })
  });

  const dados = await res.json();
  document.getElementById('mensagemVeiculo').innerText = dados.mensagem;
});

// ✅ Estacionar Veículo (corrigido para enviar cpf, placa e modelo)
document.getElementById('formEstacionar').addEventListener('submit', async function (e) {
  e.preventDefault();
  const cpf = this.cpf.value;
  const placa = this.placa.value;
  const modelo = this.modelo.value;

  const res = await fetch('/estacionar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cpf, placa, modelo })
  });

  const dados = await res.json();
  document.getElementById('mensagemEstacionar').innerText = dados.mensagem;
});

// ✅ Liberar Veículo
document.getElementById('formLiberar').addEventListener('submit', async function (e) {
  e.preventDefault();
  const cpf = this.cpf.value;
  const matricula = this.matricula.value;

  const res = await fetch('/liberar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cpf, matricula })
  });

  const dados = await res.json();
  document.getElementById('mensagemLiberar').innerText = dados.mensagem;
});

// ✅ Atualizar Status das Vagas
async function carregarVagas() {
  const res = await fetch('/vagas');
  const vagas = await res.json();
  const container = document.getElementById('vagasContainer');
  container.innerHTML = '';

  for (const vaga of vagas) {
    const div = document.createElement('div');
    div.classList.add('vaga');
    div.innerHTML = `
      <strong>Vaga ${vaga.numero}</strong><br>
      Tipo: ${vaga.tipo}<br>
      ${vaga.ocupada ? `🔴 Ocupada - ${vaga.veiculo}` : '🟢 Livre'}
    `;
    container.appendChild(div);
  }
}

// ✅ Verificar Tempo Excedido
async function verificarTempo() {
  const res = await fetch('/tempo-excedido');
  const dados = await res.json();
  document.getElementById('alertaTempo').innerText = dados.mensagem;
}
