const DIAS = ['S','T','Q','Q','S','S','D'];
const PERIODOS = ['M','T','N'];

function grelhaHTML(matriz, editavel = false){
  const classes = ['', 'is-me', 'is-them', 'is-both'];
  const vazia = [[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]];
  const dados = matriz || vazia;

  let html = '<span></span>' + DIAS.map(d => `<span class="avail-day">${d}</span>`).join('');

  dados.forEach((linha, i) => {
    html += `<span class="avail-period">${PERIODOS[i]}</span>`;
    linha.forEach((valor, d) => {
      const rotulo = `${PERIODOS[i]} de ${DIAS[d]}`;
      html += editavel
        ? `<button type="button" class="avail-cell ${classes[valor]}" data-periodo="${i}" data-dia="${d}" aria-label="${rotulo}"></button>`
        : `<span class="avail-cell ${classes[valor]}" aria-label="${rotulo}"></span>`;
    });
  });

  return html;
}

function lerGrelha(elemento){
  const m = [[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]];
  elemento.querySelectorAll('.avail-cell.is-me').forEach(c => {
    m[c.dataset.periodo][c.dataset.dia] = 1;
  });
  return m;
}

function ligarGrelha(elemento){
  elemento.addEventListener('click', e => {
    const cel = e.target.closest('.avail-cell');
    if (cel) cel.classList.toggle('is-me');
  });
}

function desenharGrelhas(){
  document.querySelectorAll('[data-grelha]').forEach(el => {
    el.innerHTML = grelhaHTML(JSON.parse(el.dataset.grelha));
  });
}
