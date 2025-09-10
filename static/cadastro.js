// Alternância de abas (login/cadastro)
const tabLogin = document.getElementById('tab-login');
const tabReg   = document.getElementById('tab-register');
const paneLogin = document.getElementById('pane-login');
const paneReg   = document.getElementById('pane-register');
const alertBox  = document.getElementById('auth-alert');

function showAlert(kind, text) {
  alertBox.className = 'alert mt-8 ' + (kind === 'error' ? 'alert--error' : 'alert--ok');
  alertBox.style.display = 'block';
  alertBox.textContent = text;
}
function clearAlert() {
  alertBox.style.display = 'none';
  alertBox.textContent = '';
}

function setActive(tab) {
  if (tab === 'login') {
    tabLogin.setAttribute('aria-selected', 'true');
    tabReg.setAttribute('aria-selected', 'false');
    paneLogin.hidden = false;
    paneReg.hidden = true;
  } else {
    tabReg.setAttribute('aria-selected', 'true');
    tabLogin.setAttribute('aria-selected', 'false');
    paneReg.hidden = false;
    paneLogin.hidden = true;
  }
  clearAlert();
}
tabLogin.addEventListener('click', () => setActive('login'));
tabReg.addEventListener('click',   () => setActive('register'));

// Botões
const btnLogin = document.getElementById('btn-login');
const btnReg   = document.getElementById('btn-register');

// Handlers
btnLogin.addEventListener('click', async () => {
  clearAlert();
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  if (!email || !password) return showAlert('error', 'Informe e-mail e senha.');

  btnLogin.disabled = true; btnLogin.textContent = 'Entrando...';
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ email, password })
    });
    const data = await res.json().catch(()=> ({}));
    if (!res.ok) {
      showAlert('error', data.error || 'Erro ao entrar.');
      btnLogin.disabled = false; btnLogin.textContent = 'Entrar';
      return;
    }
    // Sessão criada → vai direto pro teste
    window.location.href = '/teste-de-risco';
  } catch (e) {
    console.error(e);
    showAlert('error', 'Falha na comunicação com o servidor.');
    btnLogin.disabled = false; btnLogin.textContent = 'Entrar';
  }
});

btnReg.addEventListener('click', async () => {
  clearAlert();
  const name  = document.getElementById('reg-nome').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const pwd   = document.getElementById('reg-senha').value;
  const pwd2  = document.getElementById('reg-senha2').value;

  if (!name || !email || !pwd || !pwd2) return showAlert('error', 'Preencha todos os campos.');
  if (pwd.length < 6) return showAlert('error', 'A senha deve ter pelo menos 6 caracteres.');
  if (pwd !== pwd2)   return showAlert('error', 'As senhas não conferem.');

  btnReg.disabled = true; btnReg.textContent = 'Cadastrando...';
  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ name, email, password: pwd })
    });
    const data = await res.json().catch(()=> ({}));
    if (res.status === 409) {
      showAlert('error', 'E-mail já cadastrado. Tente entrar.');
      setActive('login');
      btnReg.disabled = false; btnReg.textContent = 'Criar conta';
      return;
    }
    if (!res.ok) {
      showAlert('error', data.error || 'Erro ao cadastrar.');
      btnReg.disabled = false; btnReg.textContent = 'Criar conta';
      return;
    }
    // Cadastro cria sessão no backend → segue para o teste
    window.location.href = '/teste-de-risco';
  } catch (e) {
    console.error(e);
    showAlert('error', 'Falha na comunicação com o servidor.');
    btnReg.disabled = false; btnReg.textContent = 'Criar conta';
  }
});

// Ao abrir a página, se já estiver logado, manda direto pro teste (opcional)
fetch('/api/auth/me')
  .then(r => r.ok ? r.json() : {authenticated:false})
  .then(me => { if (me.authenticated) window.location.href = '/teste-de-risco'; })
  .catch(()=>{});

// Inicia com a aba de login ativa
setActive('login');
