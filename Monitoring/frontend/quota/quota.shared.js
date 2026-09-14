(() => {
  // Constantes
  const UNIT_MULTIPLIERS = {
    bytes: 1,
    ko:    1024,
    mo:    1024 ** 2,
    go:    1024 ** 3,
    to:    1024 ** 4,
  };

  const UNIT_LABELS = [
    { key: 'bytes', label: 'Bytes' },
    { key: 'ko',    label: 'Ko'    },
    { key: 'mo',    label: 'Mo'    },
    { key: 'go',    label: 'Go'    },
    { key: 'to',    label: 'To'    },
  ];

  // Formatage
  function formatBytes(bytes) {
    const value = Number(bytes);
    if (!Number.isFinite(value) || value <= 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'Ko', 'Mo', 'Go', 'To'];
    const i = Math.min(Math.floor(Math.log(value) / Math.log(k)), sizes.length - 1);
    return parseFloat((value / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /** Décompose un nombre d'octets en { value, unit } lisibles. */
  function splitBytes(bytes) {
    const value = Math.max(0, Number(bytes) || 0);
    const orderedKeys = ['to', 'go', 'mo', 'ko', 'bytes'];
    const unit = orderedKeys.find(k => value >= UNIT_MULTIPLIERS[k]) || 'bytes';
    return {
      value: parseFloat((value / UNIT_MULTIPLIERS[unit]).toFixed(2)),
      unit,
    };
  }

  // Lecture des inputs
  function getBytesFromInputs(valueId, unitId) {
    const raw  = document.getElementById(valueId)?.value ?? '';
    const unit = document.getElementById(unitId)?.value  ?? 'bytes';
    const val  = Math.max(0, Number(raw === '' ? 0 : raw) || 0);
    return Math.round(val * (UNIT_MULTIPLIERS[unit] || 1));
  }

  // Construction du <select> d'unités
  function buildUnitsSelect(selectEl, selectedUnit = 'mo') {
    if (!selectEl) return;
    selectEl.innerHTML = '';
    UNIT_LABELS.forEach(({ key, label }) => {
      const opt = document.createElement('option');
      opt.value    = key;
      opt.textContent = label;
      if (key === selectedUnit) opt.selected = true;
      selectEl.appendChild(opt);
    });
  }

  // Panneau format lisible
  function updateFormatPanel(bytes, displayId, bytesId, isEmpty = false) {
    const displayEl = document.getElementById(displayId);
    const bytesEl   = document.getElementById(bytesId);
    if (displayEl) displayEl.textContent = isEmpty ? '—' : formatBytes(bytes);
    if (bytesEl)   bytesEl.textContent   = isEmpty ? '0 octet(s)' : Math.trunc(bytes).toLocaleString('fr-FR') + ' octet(s)';
  }

  // Remet le format-panel à zéro.
  function resetFormatPanel(displayId, bytesId) {
    updateFormatPanel(0, displayId, bytesId, true);
  }

  // Supprime une ressource via DELETE après confirmation.
  function apiDelete(url, onSuccess) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce quota ?')) return;
    fetch(url, { method: 'DELETE' })
      .then(async response => {
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Erreur serveur');
        return data;
      })
      .then(data => {
        if (data.status === 'ok') {
          alert('Quota supprimé avec succès');
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

  // Chargement des type_user sans quota
  function loadTypeUsers(selectId, hintId) {
    const sel  = document.getElementById(selectId);
    const hint = document.getElementById(hintId);
    if (!sel) return;

    sel.innerHTML = '<option value="" disabled selected>Chargement...</option>';

    fetch('http://localhost:8000/api/type_user/sans_quota')
      .then(r => r.json())
      .then(data => {
        sel.innerHTML = '';
        if (!data.data || data.data.length === 0) {
          sel.innerHTML = '<option value="" disabled selected>Aucun type disponible</option>';
          if (hint) hint.textContent = 'Tous les types ont déjà un quota.';
          return;
        }
        const placeholder = document.createElement('option');
        placeholder.value    = '';
        placeholder.disabled = true;
        placeholder.selected = true;
        placeholder.textContent = 'Sélectionnez un type user…';
        sel.appendChild(placeholder);

        data.data.forEach(tu => {
          const opt = document.createElement('option');
          opt.value       = tu.id;
          opt.textContent = tu.type_user;
          sel.appendChild(opt);
        });
        if (hint) hint.textContent = `${data.data.length} type(s) disponible(s) sans quota.`;
      })
      .catch(() => {
        sel.innerHTML = '<option value="" disabled selected>Erreur de chargement</option>';
      });
  }

  // Export global
  window.QuotaShared = {
    UNIT_MULTIPLIERS,
    formatBytes,
    splitBytes,
    getBytesFromInputs,
    buildUnitsSelect,
    updateFormatPanel,
    resetFormatPanel,
    apiDelete,
    loadTypeUsers,
  };
})();
