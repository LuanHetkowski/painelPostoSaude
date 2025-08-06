let idx = 0, avisoIdx = 0;
let imagens = [], avisos = [];

async function fetchData() {
  const [pacientes, avisosResp, imagensResp, overlayResp] = await Promise.all([
    fetch('/api/pacientes').then(r => r.json()),
    fetch('/api/avisos').then(r => r.json()),
    fetch('/api/imagens').then(r => r.json()),    
    fetch('/api/overlay').then(r => r.json()),
  ]);

  const lista = document.getElementById('pacientes-lista');
  lista.innerHTML = '';
  pacientes.forEach((p, i) => {
    const li = document.createElement('li');
    li.className = i % 2 === 0 ? 'linha-branca' : 'linha-cinza';
    li.textContent = p.sala ? `${p.nome} - Sala ${p.sala}` : p.nome;
    lista.appendChild(li);
  });

  imagens = imagensResp;
  avisos = avisosResp;

  const overlay = overlayResp.proximo || '';
  const sala = overlayResp.sala || '';
  const overlayEl = document.getElementById('overlay');
  const textEl = document.getElementById('overlay-text');
  if (overlay) {
    textEl.textContent = `PRÓXIMO: ${overlay}` + (sala ? ` - Sala ${sala}` : '');
    overlayEl.style.display = 'flex';
    document.getElementById('bipe').play();
    setTimeout(() => overlayEl.style.display = 'none', 8000);
    fetch('/admin', { method: 'POST', body: new URLSearchParams({ proximo: '' }) });
  }

  if (imagens.length > 0) {
    document.getElementById('slide').src = imagens[idx % imagens.length];
  }

  if (avisos.length > 0) {
    document.getElementById('aviso').textContent = avisos[avisoIdx % avisos.length];
  }
}

setInterval(() => {
  idx++;
  avisoIdx++;
  fetchData();
}, 8000);

fetchData();
