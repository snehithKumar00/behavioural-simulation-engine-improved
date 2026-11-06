import numpy as np
from player import Player

class SimulationEngine:
    def __init__(self, config):
        self.config = config
        self.num_players = int(config.get('num_players', 1000))
        self.days = 30

    def run(self):
        players = [Player(i, self.config['difficulty']) for i in range(self.num_players)]
        active_history = []
        daily_reasons = []
        
        X_data = []
        y_labels = []

        for day in range(1, self.days + 1):
            active_today, f_churn, b_churn, p_churn = 0, 0, 0, 0
            for p in players:
                if p.is_active:
                    p.update_state(self.config, day)
                    if p.is_active:
                        active_today += 1
                    else:
                        if p.quit_reason == "Frustration": f_churn += 1
                        elif p.quit_reason == "Boredom": b_churn += 1
                        else: p_churn += 1
            
            active_history.append(active_today)
            daily_reasons.append({'Frustration': f_churn, 'Boredom': b_churn, 'Personal': p_churn})
            
        active_final = [p for p in players if p.is_active]
        total_f_churn = sum(d['Frustration'] for d in daily_reasons)
        total_b_churn = sum(d['Boredom'] for d in daily_reasons)
        total_p_churn = sum(d['Personal'] for d in daily_reasons)
        
        for p in players:
            if p.quit_reason != "Personal":
                # Pad early exits with -99.0 for the Masking layer
                padded_history = p.history + [[-99.0, -99.0, -99.0, -99.0]] * (30 - len(p.history))
                X_data.append(padded_history)
                y_labels.append(1 if p.quit_reason in ["Frustration", "Boredom"] else 0)

        return {
            'retention_rate': round((len(active_final) / self.num_players) * 100, 1),
            'avg_lifespan': round(np.mean([p.day_quit for p in players]), 1),
            'total_churn': self.num_players - len(active_final),
            'total_f_churn': total_f_churn,
            'total_b_churn': total_b_churn,
            'total_p_churn': total_p_churn,
            'daily_active': active_history,
            'daily_churn_reasons': daily_reasons,
            'raw_players': players,
            'X_tensor': np.array(X_data),
            'y_tensor': np.array(y_labels)
        }