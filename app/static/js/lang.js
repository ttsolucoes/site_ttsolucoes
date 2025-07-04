function setLanguage(lang) {
  document.cookie = `lang=${lang};path=/;max-age=31536000`; // cookie válido por 1 ano
  location.reload(); // opcional: recarrega a página para aplicar o idioma
}

// Ao carregar a página, você pode opcionalmente ler o cookie se quiser usar aqui (não obrigatório)
document.addEventListener('DOMContentLoaded', () => {
  console.log('Idioma salvo no cookie:', getCookie('lang'));
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}
