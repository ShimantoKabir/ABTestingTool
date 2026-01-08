class ABTestingClient {
  /**
   * @param {Object} config
   * @param {string} config.serverBaseUrl - Your API server URL (e.g., "http://localhost:8000")
   * @param {number} config.projectId - The ID of the project this website belongs to
   */
  constructor(config) {
    if (!config.serverBaseUrl || !config.projectId) {
      throw new Error(
        "ABTestingSDK: serverBaseUrl and projectId are required."
      );
    }
    this.serverBaseUrl = config.serverBaseUrl;
    this.projectId = config.projectId;
    this.storageKey = "ab-end-user-id"; // Key for localStorage
  }

  async init() {
    try {
      const decisionData = await this._fetchDecision();

      // --- NEW: Save the User ID to localStorage ---
      // The server returns the ID it used (either the one we sent, or a new random one).
      // We save it so the user remains consistent on next reload.
      if (decisionData.endUserId) {
        localStorage.setItem(this.storageKey, decisionData.endUserId);
      }

      // Apply Decisions (Visual Changes)
      if (decisionData.decisions && Array.isArray(decisionData.decisions)) {
        decisionData.decisions.forEach((decision) => {
          this._applyExperiment(decision);
        });
      }
    } catch (error) {
      console.error("ABTestingSDK Error:", error);
    }
  }

  /**
   * internal: Fetch decision from backend
   */
  async _fetchDecision() {
    // 1. Read User ID from localStorage (was Cookie)
    const userId = localStorage.getItem(this.storageKey);

    const payload = {
      url: window.location.href,
      endUserId: userId ? parseInt(userId) : null,
      projectId: this.projectId,
    };

    const response = await fetch(`${this.serverBaseUrl}/decision`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch decision: ${response.statusText}`);
    }

    return await response.json();
  }

  _applyExperiment(decision) {
    // Inject CSS & JS
    if (decision.experimentCss)
      this._injectCss(decision.experimentCss, `exp-${decision.experimentId}`);
    if (decision.experimentJs) this._executeJs(decision.experimentJs);

    const variation = decision.variation;
    if (variation) {
      if (variation.css)
        this._injectCss(variation.css, `var-${variation.variationId}`);
      if (variation.js) this._executeJs(variation.js);
    }

    // Attach Metric Listeners
    if (decision.metrics && Array.isArray(decision.metrics)) {
      this._setupMetrics(decision.metrics, decision.experimentId);
    }
  }

  _injectCss(cssContent, id) {
    const style = document.createElement("style");
    style.id = `ab-style-${id}`;
    style.innerHTML = cssContent;
    document.head.appendChild(style);
  }

  _executeJs(jsContent) {
    try {
      const scriptFn = new Function(jsContent);
      scriptFn();
    } catch (e) {
      console.error("ABTestingSDK: Error executing variation JS", e);
    }
  }

  _setupMetrics(metrics, experimentId) {
    metrics.forEach((metric) => {
      if (metric.selector) {
        if (document.readyState === "loading") {
          document.addEventListener("DOMContentLoaded", () =>
            this._attachListener(metric, experimentId)
          );
        } else {
          this._attachListener(metric, experimentId);
        }
      }
    });
  }

  _attachListener(metric, experimentId) {
    const elements = document.querySelectorAll(metric.selector);
    elements.forEach((el) => {
      el.addEventListener(
        "click",
        () => {
          this._trackMetric(metric.id, experimentId);
        },
        { once: false }
      );
    });
  }

  /**
   * internal: Call the backend tracking endpoint
   * @param {number} metricId
   * @param {number} experimentId
   */
  async _trackMetric(metricId, experimentId) {
    try {
      await fetch(`${this.serverBaseUrl}/metrics/track`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          metricsId: metricId,
          experimentId: experimentId, // Pass the experimentId from the SDK,
          custom: false,
        }),
      });
      console.log(`ABTestingSDK: Metric tracked successfully`);
    } catch (error) {
      console.error("ABTestingSDK: Failed to track metric", error);
    }
  }

  /**
   * internal: Call the backend tracking endpoint
   * @param {string} eventName
   * @param {number} experimentId
   */
  async trackCustomMetric(eventName, experimentId) {
    try {
      await fetch(`${this.serverBaseUrl}/metrics/track`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          eventName: eventName,
          experimentId: experimentId, // Pass the experimentId from the SDK
          custom: true,
        }),
      });
      console.log(
        `ABTestingSDK: Custom metric ${eventName} tracked successfully`
      );
    } catch (error) {
      console.error("ABTestingSDK: Failed to track metric", error);
    }
  }
}

window.ABTestingClient = ABTestingClient;
