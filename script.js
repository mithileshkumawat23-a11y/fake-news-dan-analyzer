async function analyzeNews() {

    const newsText = document.getElementById("newsText").value;
    const result = document.getElementById("result");
    const chartBox = document.getElementById("chartBox");

    if (newsText.trim() === "") {
        result.innerHTML = "<p>Please enter some news text.</p>";
        return;
    }

    result.innerHTML = "<p>Analyzing news...</p>";
    chartBox.hidden = true;

    try {

        const response = await fetch(
            "https://fake-news-dna-analyzer.onrender.com/api/analyze",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: newsText
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || data.message || "Analysis failed."
            );
        }

        if (data.error || data.ERROR) {
            throw new Error(data.error || data.ERROR);
        }


        /* CLAIMS */

        let claimsHTML = "";

        if (data.claims && data.claims.length > 0) {

            claimsHTML = data.claims.map((claim, index) => `
                <div class="claim-item">
                    <strong>Claim ${index + 1}</strong>
                    <p>${escapeHTML(claim)}</p>
                </div>
            `).join("");

        } else {

            claimsHTML = "<p>No claims detected.</p>";

        }


        /* EVIDENCE */

        let evidenceHTML = "";

        if (data.evidence && data.evidence.length > 0) {

            evidenceHTML = data.evidence.map((item, index) => `

                <div class="evidence-item">

                    <strong>Evidence ${index + 1}</strong>

                    <p>${escapeHTML(item.title || "No title available")}</p>

                    <small>
                        Source: ${escapeHTML(item.source || "Unknown")}
                    </small>

                    <br>

                    ${safeLink(item.url, "View Source")}

                </div>

            `).join("");

        } else {

            evidenceHTML = "<p>No evidence found.</p>";

        }


        /* REFERENCE SOURCES */

        let referenceSourcesHTML = "";

        if (
            data.reference_sources &&
            data.reference_sources.length > 0
        ) {

            referenceSourcesHTML = data.reference_sources.map(
                (item, index) => `

                    <div class="evidence-item">

                        <strong>Reference ${index + 1}</strong>

                        <h4>
                            ${escapeHTML(item.title || "Untitled reference")}
                        </h4>

                        <p>
                            ${escapeHTML(item.description || "No description available.")}
                        </p>

                        ${item.excerpt
                            ? `<p>${escapeHTML(
                                item.excerpt.replace(/<[^>]*>/g, "")
                            )}</p>`
                            : ""
                        }

                        <small>
                            Source: ${escapeHTML(item.source || "Wikipedia")}
                        </small>

                        <br>

                        ${safeLink(item.url, "Read Reference")}

                    </div>

                `
            ).join("");

        } else {

            referenceSourcesHTML = `
                <p>No reference sources found for this input.</p>
            `;

        }


        /* VERIFICATION */

        let verificationHTML = "";

        if (data.verification && data.verification.length > 0) {

            verificationHTML = data.verification.map(
                (item, index) => `

                    <div class="verification-item">

                        <strong>Claim ${index + 1}</strong>

                        <p>
                            ${escapeHTML(item.status || "UNVERIFIED")}
                        </p>

                        <small>
                            Evidence Count:
                            ${Number(item.evidence_count) || 0}
                        </small>

                        <br>

                        <small>
                            Match Score:
                            ${Number(item.match_score) || 0}
                        </small>

                    </div>

                `
            ).join("");

        } else {

            verificationHTML = "<p>No verification result.</p>";

        }


        /* SHAP EXPLANATION */

        let shapHTML = "";

        if (
            data.explanation &&
            data.explanation.top_features &&
            data.explanation.top_features.length > 0
        ) {

            shapHTML = data.explanation.top_features.map(
                feature => `

                    <li>

                        <strong>
                            ${escapeHTML(feature.word || "")}
                        </strong>

                        → ${escapeHTML(feature.influence || "Unknown")}

                        <span>
                            Score: ${Number(feature.score) || 0}
                        </span>

                    </li>

                `
            ).join("");

        } else {

            shapHTML = "<li>No explanation details available.</li>";

        }


        /* CONFIDENCE AND DNA REPORT */

        const dna = data.dna_report || {};

        const confidencePercentage =
            Number(dna.confidence_percentage) ||
            Number(data.confidence) * 100 ||
            0;

        const claimsDetected =
            Number(dna.claims_detected) ||
            (data.claims ? data.claims.length : 0);

        const evidenceFound =
            Number(dna.evidence_found) ||
            (data.evidence ? data.evidence.length : 0);


        /* FINAL REPORT */

        result.innerHTML = `

            <div class="report">

                <h2>🧬 News DNA Report</h2>

                <div class="report-grid">

                    <div class="report-card">
                        <h3>Prediction</h3>
                        <p>${escapeHTML(data.prediction || "Unavailable")}</p>
                    </div>

                    <div class="report-card">
                        <h3>Risk Signal</h3>
                        <p>${escapeHTML(data.risk_signal || "Unavailable")}</p>
                    </div>

                    <div class="report-card">
                        <h3>Confidence</h3>
                        <p>${confidencePercentage.toFixed(2)}%</p>
                    </div>

                    <div class="report-card">
                        <h3>Claims Detected</h3>
                        <p>${claimsDetected}</p>
                    </div>

                    <div class="report-card">
                        <h3>Evidence Found</h3>
                        <p>${evidenceFound}</p>
                    </div>

                </div>


                <!-- FACT CHECK STATUS -->

                <div class="report-section">

                    <h3>⚖️ Fact-Check Status</h3>

                    <p>
                        ${escapeHTML(
                            data.fact_check_status || "NOT VERIFIED"
                        )}
                    </p>

                    <small>
                        ${escapeHTML(
                            data.confidence_note ||
                            "Model confidence does not prove whether a claim is true or false."
                        )}
                    </small>

                </div>


                <!-- CLAIMS -->

                <div class="report-section">

                    <h3>📌 Claim Analysis</h3>

                    ${claimsHTML}

                </div>


                <!-- NEWS EVIDENCE -->

                <div class="report-section">

                    <h3>🔎 News Evidence</h3>

                    ${evidenceHTML}

                </div>


                <!-- REFERENCE SOURCES -->

                <div class="report-section">

                    <h3>📚 Reference Sources</h3>

                    <p>
                        These pages provide background information.
                        They do not independently verify a claim.
                    </p>

                    ${referenceSourcesHTML}

                </div>


                <!-- VERIFICATION -->

                <div class="report-section">

                    <h3>⚖️ Evidence Verification</h3>

                    ${verificationHTML}

                </div>


                <!-- SHAP -->

                <div class="report-section">

                    <h3>🧠 SHAP Explanation</h3>

                    <ul>
                        ${shapHTML}
                    </ul>

                </div>

            </div>

        `;


        /* CREATE CHART */

        createDNAChart(data);

    }

    catch (error) {

        result.innerHTML = `
            <p>
                Unable to analyze the news.
                Please check whether the backend is running.
            </p>
        `;

        console.error("Analysis error:", error);

    }

}


/* ESCAPE HTML */

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");

}


/* SAFE SOURCE LINKS */

function safeLink(url, label) {

    try {

        const parsedURL = new URL(url);

        if (
            parsedURL.protocol !== "https:" &&
            parsedURL.protocol !== "http:"
        ) {
            return "";
        }

        return `
            <a
                href="${escapeHTML(parsedURL.href)}"
                target="_blank"
                rel="noopener noreferrer"
            >
                ${escapeHTML(label)}
            </a>
        `;

    } catch {

        return "";

    }

}


/* DNA CHART */

let dnaChartInstance = null;

function createDNAChart(data) {

    const chartBox = document.getElementById("chartBox");
    const ctx = document.getElementById("dnaChart");

    if (!ctx || typeof Chart === "undefined") {
        return;
    }

    const dna = data.dna_report || {};

    const confidence =
        Number(dna.confidence_percentage) ||
        Number(data.confidence) * 100 ||
        0;

    const claims =
        Number(dna.claims_detected) ||
        (data.claims ? data.claims.length : 0);

    const evidence =
        Number(dna.evidence_found) ||
        (data.evidence ? data.evidence.length : 0);

    if (dnaChartInstance) {
        dnaChartInstance.destroy();
    }

    chartBox.hidden = false;

    dnaChartInstance = new Chart(ctx, {

        type: "bar",

        data: {

            labels: [
                "Confidence (%)",
                "Claims",
                "Evidence"
            ],

            datasets: [{

                label: "News DNA",

                data: [
                    confidence,
                    claims,
                    evidence
                ]

            }]

        },

        options: {

            responsive: true,

            scales: {

                y: {
                    beginAtZero: true
                }

            }

        }

    });

}
