class ABTestingClient {
  /**
   * @param {Object} config
   * @param {string} config.baseUrl - Your API server URL (e.g., "http://localhost:8000")
   * @param {number} config.projectId - The ID of the project this website belongs to
   * @param {string} [config.mode='Live'] - 'Live' or 'QA' (for metric tracking)
   */
  constructor(config) {
    if (!config.baseUrl || !config.projectId) {
      throw new Error("ABTestingSDK: baseUrl and projectId are required.");
    }
    this.baseUrl = config.baseUrl;
    this.projectId = config.projectId;
    this.mode = config.mode || "Live";
    this.storageKey = "ab-testing-user-id";
  }

  /**
   * Initialize the SDK: Fetch decisions and apply changes.
   */
  async init() {
    try {
      const decisionData = await this._fetchDecision();

      // 1. Persist User Identity (Sticky Bucketing)
      if (decisionData.endUserId) {
        localStorage.setItem(this.storageKey, decisionData.endUserId);
      }

      // 2. Apply Decisions (Visual Changes)
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
    const userId = localStorage.getItem(this.storageKey);
    const payload = {
      url: window.location.href,
      endUserId: userId ? parseInt(userId) : null,
    };

    const response = await fetch(`${this.baseUrl}/decision`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "project-id": this.projectId.toString(), // Required by DecisionRouter.py
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch decision: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * internal: Apply CSS/JS and setup metrics for a single experiment
   */
  _applyExperiment(decision) {
    // 1. Inject Experiment-Level CSS & JS (if any)
    if (decision.experimentCss)
      this._injectCss(decision.experimentCss, `exp-${decision.experimentId}`);
    if (decision.experimentJs) this._executeJs(decision.experimentJs);

    // 2. Inject Variation-Level CSS & JS
    const variation = decision.variation;
    if (variation) {
      if (variation.css)
        this._injectCss(variation.css, `var-${variation.variationId}`);
      if (variation.js) this._executeJs(variation.js);
    }

    // 3. Attach Metric Listeners
    if (decision.metrics && Array.isArray(decision.metrics)) {
      this._setupMetrics(decision.metrics);
    }
  }

  /**
   * internal: Inject CSS into the head
   */
  _injectCss(cssContent, id) {
    const style = document.createElement("style");
    style.id = `ab-style-${id}`;
    style.innerHTML = cssContent;
    document.head.appendChild(style);
  }

  /**
   * internal: Execute JS safely
   */
  _executeJs(jsContent) {
    try {
      // Create a function wrapper to prevent scope pollution
      const scriptFn = new Function(jsContent);
      scriptFn();
    } catch (e) {
      console.error("ABTestingSDK: Error executing variation JS", e);
    }
  }

  /**
   * internal: Find elements by selector and attach tracking events
   */
  _setupMetrics(metrics) {
    metrics.forEach((metric) => {
      // Only track if it's a DOM interaction metric (has a selector)
      if (metric.selector) {
        // Wait for DOM to be ready just in case elements aren't loaded yet
        if (document.readyState === "loading") {
          document.addEventListener("DOMContentLoaded", () =>
            this._attachListener(metric)
          );
        } else {
          this._attachListener(metric);
        }
      }
    });
  }

  _attachListener(metric) {
    const elements = document.querySelectorAll(metric.selector);
    elements.forEach((el) => {
      el.addEventListener(
        "click",
        () => {
          this._trackMetric(metric.id);
        },
        { once: false }
      ); // Prevent spamming counts on double-click
    });
  }

  /**
   * internal: Call the backend tracking endpoint
   */
  async _trackMetric(metricId) {
    try {
      // Uses the 'mode' param we added earlier (QA vs Live)
      await fetch(
        `${this.baseUrl}/metrics/${metricId}/track?mode=${this.mode}`,
        {
          method: "POST",
        }
      );
      console.log(
        `ABTestingSDK: Metric ${metricId} tracked successfully [${this.mode}]`
      );
    } catch (error) {
      console.error("ABTestingSDK: Failed to track metric", error);
    }
  }
}

// Attach to window for global usage
window.ABTestingClient = ABTestingClient;
