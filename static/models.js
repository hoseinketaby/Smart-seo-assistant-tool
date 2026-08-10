const presetSelect = document.getElementById("preset_key");
const baseUrlField = document.getElementById("baseUrlField");
const baseUrlInput = document.getElementById("base_url");
const providerHint = document.getElementById("providerHint");
const providerWarning = document.getElementById("providerWarning");
const submitBtn = document.getElementById("submitProviderBtn");

function updateForSelectedPreset() {
  const preset = window.PROVIDER_PRESETS[presetSelect.value];
  if (!preset) return;

  const isCustom = !!preset.custom_base_url;
  baseUrlField.style.display = isCustom ? "flex" : "none";
  baseUrlInput.required = isCustom;

  if (preset.supported === false) {
    providerWarning.textContent = preset.warning;
    providerWarning.style.display = "block";
    providerHint.style.display = "none";
    submitBtn.disabled = true;
  } else {
    providerWarning.style.display = "none";
    submitBtn.disabled = false;

    if (preset.model_hint) {
      providerHint.textContent = preset.model_hint;
      providerHint.style.display = "block";
    } else {
      providerHint.style.display = "none";
    }
  }
}

presetSelect.addEventListener("change", updateForSelectedPreset);
updateForSelectedPreset();
