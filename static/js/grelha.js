/**
 * Gestão visual e interativa da grelha de disponibilidade semanal (3 períodos x 7 dias).
 * Dias: Segunda (S), Terça (T), Quarta (Q), Quinta (Q), Sexta (S), Sábado (S), Domingo (D).
 * Períodos: Manhã (M), Tarde (T), Noite (N).
 */

const DIAS = ['S', 'T', 'Q', 'Q', 'S', 'S', 'D'];
const PERIODOS = ['M', 'T', 'N'];

/**
 * Gera o HTML dos blocos da grelha.
 * @param {Array<Array<number>>} matriz - Matriz 3x7 de valores (0: vazio, 1: utilizador, 2: grupo, 3: ambos).
 * @param {boolean} editavel - Se verdadeiro, renderiza botões clicáveis para seleção.
 * @returns {string} Código HTML da grelha.
 */
function grelhaHTML(matriz, editavel = false) {
  const classes = ['', 'is-me', 'is-them', 'is-both'];
  const vazia = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0]
  ];
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

/**
 * Lê o estado atual dos blocos selecionados na grelha e devolve a matriz 3x7.
 * @param {HTMLElement} elemento - O contentor da grelha.
 * @returns {Array<Array<number>>} Matriz com 1 nos blocos selecionados e 0 nos restantes.
 */
function lerGrelha(elemento) {
  const m = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0]
  ];
  elemento.querySelectorAll('.avail-cell.is-me').forEach(c => {
    m[c.dataset.periodo][c.dataset.dia] = 1;
  });
  return m;
}

/**
 * Adiciona o ouvinte de clique para permitir selecionar/desmarcar blocos de horário.
 * @param {HTMLElement} elemento - O contentor da grelha.
 */
function ligarGrelha(elemento) {
  elemento.addEventListener('click', e => {
    const cel = e.target.closest('.avail-cell');
    if (cel) cel.classList.toggle('is-me');
  });
}

/**
 * Renderiza automaticamente todas as grelhas estáticas (somente leitura) presentes na página.
 */
function desenharGrelhas() {
  document.querySelectorAll('[data-grelha]').forEach(el => {
    try {
      const dados = JSON.parse(el.dataset.grelha);
      el.innerHTML = grelhaHTML(dados);
    } catch (e) {
      el.innerHTML = grelhaHTML(null);
    }
  });
}
