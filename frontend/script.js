const API_BASE = "http://localhost:8000";

async function analyzeEmail() {

    const email = document
        .getElementById("emailInput")
        .value;

    if (!email.trim()) {
        alert("Please enter email content");
        return;
    }

    try {

        showLoading();

        const response = await fetch(
            `${API_BASE}/predict`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email
                })
            }
        );

        const data = await response.json();

        renderResult(data);

    } catch (err) {

        console.error(err);

        alert("Server error");

    } finally {

        hideLoading();
    }
}

async function analyzeBatch() {

    const areas = document.querySelectorAll(
        ".batch-textarea"
    );

    const emails = [];

    areas.forEach(area => {

        if (area.value.trim()) {
            emails.push(area.value);
        }
    });

    const response = await fetch(
        `${API_BASE}/batch-predict`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                emails: emails
            })
        }
    );

    const data = await response.json();

    console.log(data);
}