// Sélection des éléments HTML par leur ID
const openBtn = document.getElementById('openBtn');
const closeBtn = document.getElementById('closeBtn');
const overlay = document.getElementById('overlay');
const dialog = document.getElementById('dialog');

// Ouvre la fenêtre modale
openBtn?.addEventListener('click', () => {
  overlay.classList.add('active');
  dialog.classList.add('active');
});

// Ferme la fenêtre modale via le bouton "Fermer"
closeBtn?.addEventListener('click', () => {
  dialog.classList.remove('active');
  overlay.classList.remove('active');
});

// Ferme la fenêtre modale en cliquant en dehors du dialogue
overlay?.addEventListener('click', (e) => {
  if (e.target === overlay) {
    dialog.classList.remove('active');
    overlay.classList.remove('active');
  }
});
