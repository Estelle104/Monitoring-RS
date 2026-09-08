(() => {
  // Couleur de la barre de progression selon le pourcentage
  function getProgressGradient(percent) {
    const p = Math.max(0, Math.min(100, Number(percent) || 0));
    if (p < 50)  return 'linear-gradient(90deg, #4ade80 0%, #86efac 100%)';
    if (p < 75)  return 'linear-gradient(90deg, #84cc16 0%, #facc15 100%)';
    if (p < 100) return 'linear-gradient(90deg, #f59e0b 0%, #f97316 55%, #ef4444 100%)';
    return 'linear-gradient(90deg, #ef4444 0%, #b91c1c 100%)';
  }

  // Échappe les caractères spéciaux HTML pour usage dans innerHTML
  function escapeHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  // Charge la liste des machines sans quota_machine dans un <select>
  function loadMachines(selectId, hintId) {
    const sel  = document.getElementById(selectId);
    const hint = document.getElementById(hintId);
    if (!sel) return;

    sel.innerHTML = '<option value="" disabled selected>Chargement...</option>';

    fetch('http://localhost:8000/api/machine/sans_quota_machine')
      .then(r => r.json())
      .then(data => {
        sel.innerHTML = '';
        if (!data.data || data.data.length === 0) {
          sel.innerHTML = '<option value="" disabled selected>Aucune machine disponible</option>';
          if (hint) hint.textContent = 'Toutes les machines ont déjà un quota machine.';
          return;
        }
        const placeholder = document.createElement('option');
        placeholder.value    = '';
        placeholder.disabled = true;
        placeholder.selected = true;
        placeholder.textContent = 'Sélectionnez une machine…';
        sel.appendChild(placeholder);

        data.data.forEach(m => {
          const opt = document.createElement('option');
          opt.value = m.id;
          const etu = m.etu ? ` ETU${m.etu}` : '';
          opt.textContent = `${m.hostname || 'Sans nom'}${etu}`;
          sel.appendChild(opt);
        });
        if (hint) hint.textContent = `${data.data.length} machine(s) disponible(s) sans quota.`;
      })
      .catch(() => {
        sel.innerHTML = '<option value="" disabled selected>Erreur de chargement</option>';
      });
  }

  // Supprime un quota machine via DELETE après confirmation
  function apiDeleteQM(url, onSuccess) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce quota machine ?')) return;
    fetch(url, { method: 'DELETE' })
      .then(async response => {
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Erreur serveur');
        return data;
      })
      .then(data => {
        if (data.status === 'ok') {
          alert('Quota machine supprimé avec succès');
          if (typeof onSuccess === 'function') onSuccess(data);
        } else {
          alert('Erreur lors de la suppression: ' + (data.detail || 'Erreur inconnue'));
        }
      })
      .catch(error => {
        console.error('Erreur:', error);
        alert('Une erreur est survenue: ' + error.message);
      });
  }

  // Export global
  window.QuotaMachineShared = {
    getProgressGradient,
    escapeHtml,
    loadMachines,
    apiDeleteQM,
  };
})();
