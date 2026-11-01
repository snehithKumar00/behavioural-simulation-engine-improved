// 1. THIS IS THE MISSING LOGIC: It connects the sliders to the blue badges
document.addEventListener('DOMContentLoaded', () => {
    const ids = ['difficulty', 'difficulty_growth', 'reward_amount', 'penalty_on_failure', 'num_players'];
    
    ids.forEach(id => {
        const slider = document.getElementById(id);
        const label = document.getElementById('val_' + id);
        
        if (slider && label) {
            // Set initial value
            label.innerText = slider.value;
            // Update value whenever the slider moves
            slider.oninput = () => {
                label.innerText = slider.value;
            };
        }
    });
});

// 2. THE SIMULATION ENGINE LOGIC
document.getElementById('runBtn').onclick = async function() {
    this.innerText = "GENERATING REPORT...";
    this.disabled = true;

    // Gather all the slider values
    const payload = {
        difficulty: parseFloat(document.getElementById('difficulty').value),
        difficulty_growth: parseFloat(document.getElementById('difficulty_growth').value),
        reward_amount: parseFloat(document.getElementById('reward_amount').value),
        penalty_on_failure: parseFloat(document.getElementById('penalty_on_failure').value),
        num_players: parseInt(document.getElementById('num_players').value)
    };

    try {
        const res = await fetch('/run_simulation', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        
        // Update top UI statistics
        document.getElementById('res_retention').innerText = data.retention_rate + "%";
        document.getElementById('res_lifespan').innerText = data.avg_lifespan;
        document.getElementById('res_churn').innerText = data.total_churn;

        // Reveal the report section
        document.getElementById('waitingState').style.display = 'none';
        document.getElementById('analyticsReport').style.display = 'block';

        // Render the 3 Base64 image charts
        document.getElementById('img_plot1').src = `data:image/png;base64,${data.plot1}`;
        document.getElementById('img_plot2').src = `data:image/png;base64,${data.plot2}`;
        document.getElementById('img_plot3').src = `data:image/png;base64,${data.plot3}`;

        // --- DYNAMIC INSIGHTS GENERATION ---
        
        let insight1 = data.retention_rate >= 70 ? `<strong>System Healthy:</strong> A retention rate of ${data.retention_rate}% indicates balanced difficulty.` : 
                       data.retention_rate >= 30 ? `<strong>Moderate Decay:</strong> Average lifespan of ${data.avg_lifespan} indicates mid-game hurdles.` : 
                       `<strong>System Collapse:</strong> Mass exodus of ${data.total_churn} agents. Difficulty outpaced learning.`;
        document.getElementById('insight_plot1').innerHTML = insight1;

        let insight2 = `<strong>Churn Breakdown:</strong> ${data.total_f_churn} agents quit due to Frustration, ${data.total_b_churn} due to Boredom, and ${data.total_p_churn} uninstalled due to External/Life reasons.`;
        document.getElementById('insight_plot2').innerHTML = insight2;

        document.getElementById('insight_plot3').innerHTML = `<strong>Population Distribution:</strong> Heatmap of the surviving agents.`;

        // --- MACHINE LEARNING RENDERER ---
        function buildMLCards(containerId, archetypesArray) {
            const container = document.getElementById(containerId);
            container.innerHTML = ''; 
            
            if (archetypesArray && archetypesArray.length > 0) {
                archetypesArray.forEach(arch => {
                    // Set specific colors based on the trait
                    let badgeColor = 'bg-secondary'; // Default for External Factors
                    if (arch.dominant_emotion === 'Frustration') badgeColor = 'bg-danger';
                    else if (arch.dominant_emotion === 'Boredom') badgeColor = 'bg-warning text-dark';
                    else if (arch.dominant_emotion === 'External Factors') badgeColor = 'bg-secondary text-white';
                    
                    // Override to Green for positive survivor names
                    if (arch.name.includes("Flow") || arch.name.includes("Casual") || arch.name.includes("Tier")) badgeColor = 'bg-success';

                    container.innerHTML += `
                        <div class="col-md-4 mb-3">
                            <div class="card bg-dark border-secondary h-100 p-3 shadow">
                                <h6 class="text-white fw-bold">${arch.name}</h6>
                                <h2 class="text-info mb-0">${arch.population} <span class="fs-6 text-light opacity-75">Agents</span></h2>
                                <hr class="border-secondary my-2">
                                <small class="text-light d-block opacity-75">Avg Skill Level: <span class="text-white fw-bold">${arch.avg_skill}</span></small>
                                <span class="badge ${badgeColor} mt-2 w-100 py-2">Dominant Trait: ${arch.dominant_emotion}</span>
                            </div>
                        </div>
                    `;
                });
            } else {
                container.innerHTML = `<p class="text-muted">Not enough data to calculate clusters.</p>`;
            }
        }

        // Build the two rows of ML cards
        buildMLCards('ml_survivors', data.arch_survivors);
        buildMLCards('ml_churned', data.arch_churned);

    } catch (e) {
        alert("Simulation Error. Check Terminal for backend Python errors.");
        console.error(e);
    } finally {
        // Reset the button
        this.innerText = "RUN SYSTEM TEST";
        this.disabled = false;
    }
};