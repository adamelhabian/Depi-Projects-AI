/**
 * CharityML Donor Intelligence - Frontend UX Interactions
 * Handles preset filling, education-num syncing, and accessibility enhancements.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Education Level to Education-Num mapping based on Census dataset
  const EDUCATION_MAP = {
    'Preschool': 1,
    '1st-4th': 2,
    '5th-6th': 3,
    '7th-8th': 4,
    '9th': 5,
    '10th': 6,
    '11th': 7,
    '12th': 8,
    'HS-grad': 9,
    'Some-college': 10,
    'Assoc-voc': 11,
    'Assoc-acdm': 12,
    'Bachelors': 13,
    'Masters': 14,
    'Prof-school': 15,
    'Doctorate': 16
  };

  const form = document.getElementById('prediction-form');
  const educationSelect = document.getElementById('education_level');
  const educationNumInput = document.getElementById('education-num');
  const resultsContainer = document.getElementById('results-container');

  // Auto-sync education-num when education_level changes
  if (educationSelect && educationNumInput) {
    educationSelect.addEventListener('change', (e) => {
      const selectedLevel = e.target.value;
      if (EDUCATION_MAP[selectedLevel] !== undefined) {
        educationNumInput.value = EDUCATION_MAP[selectedLevel];
      }
    });
  }

  // Pre-configured realistic sample profiles for easy testing
  const PRESET_PROFILES = {
    highIncome: {
      'age': 45,
      'workclass': 'Private',
      'education_level': 'Bachelors',
      'education-num': 13,
      'marital-status': 'Married-civ-spouse',
      'occupation': 'Exec-managerial',
      'relationship': 'Husband',
      'race': 'White',
      'sex': 'Male',
      'capital-gain': 7298,
      'capital-loss': 0,
      'hours-per-week': 48,
      'native-country': 'United-States'
    },
    techSpecialist: {
      'age': 38,
      'workclass': 'Private',
      'education_level': 'Masters',
      'education-num': 14,
      'marital-status': 'Married-civ-spouse',
      'occupation': 'Prof-specialty',
      'relationship': 'Wife',
      'race': 'White',
      'sex': 'Female',
      'capital-gain': 5178,
      'capital-loss': 0,
      'hours-per-week': 45,
      'native-country': 'United-States'
    },
    standardIncome: {
      'age': 25,
      'workclass': 'Private',
      'education_level': 'Some-college',
      'education-num': 10,
      'marital-status': 'Never-married',
      'occupation': 'Adm-clerical',
      'relationship': 'Own-child',
      'race': 'White',
      'sex': 'Female',
      'capital-gain': 0,
      'capital-loss': 0,
      'hours-per-week': 38,
      'native-country': 'United-States'
    }
  };

  // Preset button listeners
  const presetButtons = document.querySelectorAll('[data-preset]');
  presetButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const presetName = btn.getAttribute('data-preset');
      const profile = PRESET_PROFILES[presetName];

      if (!profile || !form) return;

      Object.entries(profile).forEach(([key, val]) => {
        const input = form.elements[key];
        if (input) {
          input.value = val;
        }
      });

      // Visual feedback
      btn.style.transform = 'scale(0.95)';
      setTimeout(() => {
        btn.style.transform = '';
      }, 150);
    });
  });

  // Reset button listener
  const resetBtn = document.getElementById('btn-reset');
  if (resetBtn && form) {
    resetBtn.addEventListener('click', (e) => {
      e.preventDefault();
      form.reset();
      if (educationNumInput) educationNumInput.value = '10';
    });
  }

  // Smooth scroll to results if present on load
  if (resultsContainer && resultsContainer.children.length > 0) {
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
});
