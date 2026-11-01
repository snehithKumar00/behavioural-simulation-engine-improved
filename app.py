from flask import Flask, render_template, request, jsonify
import io, base64, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from engine import SimulationEngine
from ml_analytics import analyze_player_archetypes

app = Flask(__name__)

def plot_to_base64(fig):
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#05070a', bbox_inches='tight')
    img.seek(0)
    plt.close(fig)
    return base64.b64encode(img.getvalue()).decode()

def generate_visuals(results):
    plt.style.use('dark_background')
    days = range(30)
    
    # 1. Retention Curve
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    fig1.patch.set_facecolor('#05070a')
    ax1.plot(days, results['daily_active'], color='#00d4ff', linewidth=3)
    ax1.fill_between(days, results['daily_active'], color='#00d4ff', alpha=0.1)
    ax1.set_title("Population Survival Over 30 Days", color='#00d4ff')
    ax1.set_ylabel("Active Agents")
    ax1.set_ylim(0, max(results['daily_active']) + 50)
    plot1 = plot_to_base64(fig1)

    # 2. Churn Causes 
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    fig2.patch.set_facecolor('#05070a')
    b_churn = [d['Boredom'] for d in results['daily_churn_reasons']]
    f_churn = [d['Frustration'] for d in results['daily_churn_reasons']]
    p_churn = [d['Personal'] for d in results['daily_churn_reasons']]
    
    ax2.stackplot(days, b_churn, f_churn, p_churn, 
                  labels=['Boredom', 'Frustration', 'External/Life Factors'], 
                  colors=['#f1c40f', '#e74c3c', '#95a5a6'], alpha=0.8)
    ax2.set_title("Volume of Quit Events by Cause", color='#00d4ff')
    ax2.legend(loc='upper right')
    plot2 = plot_to_base64(fig2)

    # 3. Hexbin Density
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    fig3.patch.set_facecolor('#05070a')
    s_final = [p.skill for p in results['raw_players']]
    f_final = [p.frustration for p in results['raw_players']]
    hb = ax3.hexbin(s_final, f_final, gridsize=15, cmap='winter', mincnt=1)
    ax3.set_title("Final State: Skill vs Accumulated Frustration", color='#00d4ff')
    ax3.set_xlabel("Agent Skill Level")
    ax3.set_ylabel("Frustration Level")
    fig3.colorbar(hb, ax=ax3)
    plot3 = plot_to_base64(fig3)

    return plot1, plot2, plot3

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    try:
        config = request.json
        res = SimulationEngine(config).run()
        p1, p2, p3 = generate_visuals(res)
        
        survivors = [p for p in res['raw_players'] if p.is_active]
        
        # We pass ALL inactive players to ML so the total numbers match the UI exactly
        churned = [p for p in res['raw_players'] if not p.is_active]
        
        arch_survivors = analyze_player_archetypes(survivors, num_clusters=3, group_type="survivors")
        
        arch_churned = []
        if len(churned) >= 3:
            arch_churned = analyze_player_archetypes(churned, num_clusters=3, group_type="churned")

        return jsonify({
            'retention_rate': res['retention_rate'],
            'avg_lifespan': f"{res['avg_lifespan']}d",
            'total_churn': res['total_churn'],
            'total_f_churn': res['total_f_churn'],
            'total_b_churn': res['total_b_churn'],
            'total_p_churn': res['total_p_churn'],
            'plot1': p1, 'plot2': p2, 'plot3': p3,
            'arch_survivors': arch_survivors,
            'arch_churned': arch_churned
        })
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)