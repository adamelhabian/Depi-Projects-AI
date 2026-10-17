
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("prediction-form");
  const resultsContainer = document.getElementById("results-container");

  // ==========================================
  // 1. Show Loading, Error, and Prediction UI
  // ==========================================

  function showResult(message, type = "info") {
    if (!resultsContainer) {
      console.log(message);
      return;
    }

    resultsContainer.replaceChildren();
    resultsContainer.className = "results-container";
    resultsContainer.hidden = false;

    // Loading and error messages
    if (type === "info" || type === "error") {
      const alert = document.createElement("div");
      alert.className = `prediction-alert ${type}`;

      const icon = document.createElement("span");
      icon.className = "prediction-alert-icon";
      icon.textContent = type === "error" ? "⚠" : "⏳";

      const text = document.createElement("p");
      text.textContent = message;

      alert.append(icon, text);
      resultsContainer.appendChild(alert);
      return;
    }

    // Prediction result
    const isHighIncome = message.includes(">50K");
    const category = isHighIncome ? "> $50K" : "≤ $50K";

    const card = document.createElement("article");
    card.className = `prediction-card ${
      isHighIncome ? "high-income" : "standard-income"
    }`;

    // Card header
    const header = document.createElement("div");
    header.className = "prediction-card-header";

    const icon = document.createElement("div");
    icon.className = "prediction-icon";
    icon.textContent = isHighIncome ? "↗" : "✓";

    const headingGroup = document.createElement("div");

    const eyebrow = document.createElement("p");
    eyebrow.className = "prediction-eyebrow";
    eyebrow.textContent = "PREDICTION COMPLETE";

    const heading = document.createElement("h3");
    heading.textContent = isHighIncome
      ? "High Income Category"
      : "Standard Income Category";

    headingGroup.append(eyebrow, heading);
    header.append(icon, headingGroup);

    // Divider
    const divider = document.createElement("div");
    divider.className = "prediction-divider";

    // Result label
    const resultLabel = document.createElement("p");
    resultLabel.className = "prediction-result-label";
    resultLabel.textContent = "Predicted annual income";

    // Result value
    const resultValue = document.createElement("p");
    resultValue.className = "prediction-result-value";
    resultValue.textContent = category;

    // Description
    const description = document.createElement("p");
    description.className = "prediction-description";
    description.textContent = isHighIncome
      ? "The model classified this profile in the income category above $50,000."
      : "The model classified this profile in the income category of $50,000 or less.";

    // Result badge
    const footer = document.createElement("div");
    footer.className = "prediction-footer";

    const badge = document.createElement("span");
    badge.className = "prediction-badge";
    badge.textContent = isHighIncome
      ? "High Income"
      : "Standard Income";

    footer.appendChild(badge);

    // Assemble card
    card.append(
      header,
      divider,
      resultLabel,
      resultValue,
      description,
      footer
    );

    resultsContainer.appendChild(card);

    // Scroll smoothly to the result
    resultsContainer.scrollIntoView({
      behavior: "smooth",
      block: "center"
    });
  }

  // ==========================================
  // 2. Collect Form Data
  // ==========================================

  function getFormData() {
    const formData = new FormData(form);
    const payload = {};

    formData.forEach((value, key) => {
      payload[key] = value;
    });

    // Convert numeric fields to numbers
    const integerFields = [
      "age",
      "education-num",
      "hours-per-week"
    ];

    const decimalFields = [
      "capital-gain",
      "capital-loss"
    ];

    integerFields.forEach((field) => {
      if (payload[field] !== undefined) {
        payload[field] = Number(payload[field]);
      }
    });

    decimalFields.forEach((field) => {
      if (payload[field] !== undefined) {
        payload[field] = Number(payload[field]);
      }
    });

    return payload;
  }

  // ==========================================
  // 3. Submit Form and Get Prediction
  // ==========================================

  if (form) {
    form.addEventListener("submit", async (event) => {
      // Prevent normal browser form submission
      event.preventDefault();

      // Validate required fields
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      const submitButton = form.querySelector(
        'button[type="submit"], input[type="submit"]'
      );

      const originalButtonText = submitButton
        ? submitButton.textContent
        : "";

      try {
        // Disable button while predicting
        if (submitButton) {
          submitButton.disabled = true;

          if (submitButton.tagName === "BUTTON") {
            submitButton.textContent = "Analyzing...";
          }
        }

        showResult(
          "Analyzing the donor profile. Please wait...",
          "info"
        );

        const payload = getFormData();

        // Send JSON to FastAPI
        const response = await fetch("/predict", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json"
          },
          body: JSON.stringify(payload)
        });

        // Read server response
        const data = await response.json();

        // Handle API errors
        if (!response.ok) {
          let errorMessage = "Prediction failed. Please try again.";

          if (data.detail) {
            if (Array.isArray(data.detail)) {
              errorMessage = data.detail
                .map((error) => error.msg)
                .join(", ");
            } else if (typeof data.detail === "string") {
              errorMessage = data.detail;
            }
          }

          throw new Error(errorMessage);
        }

        // Display prediction
        if (!data.income_category) {
          throw new Error(
            "The server response does not contain an income category."
          );
        }

        showResult(
          `Predicted income category: ${data.income_category}`,
          "success"
        );
      } catch (error) {
        console.error("Prediction error:", error);

        showResult(
          error.message ||
            "An unexpected error occurred. Please try again.",
          "error"
        );
      } finally {
        // Re-enable button
        if (submitButton) {
          submitButton.disabled = false;

          if (submitButton.tagName === "BUTTON") {
            submitButton.textContent =
              originalButtonText || "Predict Income";
          }
        }
      }
    });
  }

  // ==========================================
  // 4. Reset Form and Results
  // ==========================================

  const resetButton = document.getElementById("reset-button");

  if (resetButton) {
    resetButton.addEventListener("click", () => {
      if (form) {
        form.reset();
      }

      if (resultsContainer) {
        resultsContainer.replaceChildren();
        resultsContainer.hidden = true;
      }
    });
  }

  // ==========================================
  // 5. Preset Buttons
  // ==========================================

  const presetButtons = document.querySelectorAll("[data-preset]");

  presetButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const presetName = button.dataset.preset;

      const presets = {
        low: {
          age: 25,
          workclass: "Private",
          education_level: "HS-grad",
          "education-num": 9,
          "marital-status": "Never-married",
          occupation: "Other-service",
          relationship: "Not-in-family",
          race: "White",
          sex: "Male",
          "capital-gain": 0,
          "capital-loss": 0,
          "hours-per-week": 35,
          "native-country": "United-States"
        },

        high: {
          age: 45,
          workclass: "Private",
          education_level: "Bachelors",
          "education-num": 13,
          "marital-status": "Married-civ-spouse",
          occupation: "Exec-managerial",
          relationship: "Husband",
          race: "White",
          sex: "Male",
          "capital-gain": 15000,
          "capital-loss": 0,
          "hours-per-week": 50,
          "native-country": "United-States"
        }
      };

      const preset = presets[presetName];

      if (!preset || !form) {
        return;
      }

      Object.entries(preset).forEach(([name, value]) => {
        const field = form.elements.namedItem(name);

        if (field) {
          field.value = value;
        }
      });

      if (resultsContainer) {
        resultsContainer.replaceChildren();
        resultsContainer.hidden = true;
      }
    });
  });

  console.log("CharityML main.js loaded successfully.");
});
