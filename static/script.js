// script.js

// Função genérica de animação de números
function animateCounter(id, end, duration) {
  let element = document.getElementById(id);
  if (!element) return; // Evita erro se o elemento não existir
  let start = 0;
  let increment = end / (duration / 16); // 16ms ~ 60fps
  let current = start;

  function updateCounter() {
    current += increment;
    if (current >= end) {
      element.textContent = end.toLocaleString("pt-BR");
    } else {
      element.textContent = Math.floor(current).toLocaleString("pt-BR");
      requestAnimationFrame(updateCounter);
    }
  }
  requestAnimationFrame(updateCounter);
}

document.addEventListener('DOMContentLoaded', function () {
  const seletorEstado = document.getElementById('seletor-estado');
  const mapa = document.getElementById('map');
  const infoBox = document.getElementById('info-estado');

  // Função para buscar dados e atualizar o HTML
  async function atualizarInfoEstado(sigla) {
    infoBox.innerHTML = `<h3>Carregando dados...</h3>`;
    
    try {
      const response = await fetch(`/api/estado/${sigla}`);
      
      if (!response.ok) {
        throw new Error('Estado não encontrado');
      }

      const data = await response.json();

      infoBox.innerHTML = `
        <h3>${data.nome}</h3>
        <ul>
          <li>${data.nome} - ${data.casos} feminicídios</li>
          <li>
            <a href="${data.url_rede_ajuda}" target="_blank" rel="noopener noreferrer">
              Rede de atendimento à mulher
            </a>
          </li>
        </ul>
      `;

      seletorEstado.value = sigla;
      document.querySelectorAll('.state.active').forEach(el => el.classList.remove('active'));
      document.getElementById(`state_${sigla}`).classList.add('active');

    } catch (error) {
      console.error("Erro ao buscar dados:", error);
      infoBox.innerHTML = `<h3>Erro ao carregar dados</h3><p>Não foi possível encontrar as informações para este estado.</p>`;
    }
  }

  // Clique no mapa
  mapa.querySelectorAll('.state').forEach(estado => {
    estado.addEventListener('click', function (event) {
      event.preventDefault();
      const sigla = this.dataset.state;
      atualizarInfoEstado(sigla);
    });
  });

  // Mudança no seletor
  seletorEstado.addEventListener('change', function () {
    const sigla = this.value;
    if (sigla) {
      atualizarInfoEstado(sigla);
    }
  });

  animateCounter("fem-count", 4145, 6000);
});

document.addEventListener('click', async (e) => {
  const btn = e.target.closest('#btnLogout');
  if (!btn) return;

  btn.disabled = true; btn.textContent = 'Saindo...';
  try {
    const res = await fetch('/api/auth/logout', { method: 'POST' });
    // Depois de sair, volta a mostrar "Cadastro" automaticamente
    window.location.reload();
  } catch (err) {
    console.error(err);
    btn.disabled = false; btn.textContent = 'Sair';
    alert('Falha ao sair. Tente novamente.');
  }
});

document.addEventListener('click', async (e) => {
  if (e.target.id === 'btnLogout') {
    e.target.disabled = true;
    e.target.textContent = 'Saindo...';
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.reload();
    } catch (err) {
      console.error(err);
      e.target.disabled = false;
      e.target.textContent = 'Sair';
      alert('Erro ao sair.');
    }
  }
});

