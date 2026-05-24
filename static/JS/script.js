document.getElementById('solve-button').addEventListener('click', async () => {
    const equation = document.getElementById('equation').value;
    const interval = document.getElementById('interval').value.split(',').map(Number);
    const method = document.getElementById('method').value;

    // Send POST request to the Flask server
    const response = await fetch('/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ equation, interval, method })
    });

    const result = await response.json();

    if (result.error) {
        document.getElementById('result').innerText = `Error: ${result.error}`;
        return;
    }

    if (method === "All") {
        const methods = Object.keys(result);
        const labels = Array.from({ length: Math.max(...methods.map(m => result[m].errors.length)) }, (_, i) => `Iteration ${i + 1}`);
        
        // Colors for each method
        const colors = [
            'rgba(255, 99, 132, 0.6)', // Bisection
            'rgba(54, 162, 235, 0.6)', // Newton-Raphson
            'rgba(255, 206, 86, 0.6)', // Secant
            'rgba(75, 192, 192, 0.6)'  // Regular False Position
        ];

        // Create datasets for the chart
        const datasets = methods.map((m, i) => ({
            label: m,
            data: result[m].errors,
            fill: false,
            backgroundColor: colors[i],
            borderColor: colors[i].replace('0.6', '1'),
            borderWidth: 1,
            tension: 0.1
        }));

        // Render the comparative chart
        const ctx = document.getElementById('comparative-chart').getContext('2d');
        if (window.comparativeChart) window.comparativeChart.destroy(); // Destroy the previous chart if it exists
        window.comparativeChart = new Chart(ctx, {
            type: 'line',
            data: { labels, datasets },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true },
                    title: { display: true, text: 'Comparative Error Analysis' },
                },
                scales: {
                    x: { title: { display: true, text: 'Iterations' } },
                    y: { 
                        beginAtZero: true, 
                        title: { display: true, text: 'Error' },
                        type: 'logarithmic', // Logarithmic scale for better visualization
                    },
                },
            },
        });
    } else {
        // Display the root for the selected method
        const root = result[method].root;
        document.getElementById('result').innerText = `Root (${method}): ${root}`;
    }
});
