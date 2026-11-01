import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def analyze_player_archetypes(players, num_clusters=3, group_type="survivors"):
    if len(players) < num_clusters:
        return []

    features = np.array([[p.skill, p.frustration, p.boredom] for p in players])
    
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(scaled_features)
    
    scaled_centers = kmeans.cluster_centers_
    original_centers = scaler.inverse_transform(scaled_centers)

    archetypes = []
    used_names = {} 

    for i in range(num_clusters):
        count = int(np.sum(labels == i))
        c_skill, c_frust, c_bored = original_centers[i]
        
        dominant_emotion = "Frustration" if c_frust > c_bored else "Boredom"
        
        if group_type == "survivors":
            if c_skill > 55 and c_frust <= 15: name = "Flow-State Masters"
            elif c_frust > 15: name = "Struggling Grinders"
            elif c_bored > 15: name = "Bored Veterans"
            else: name = "The Casual Core"
        else: # group_type == "churned"
            
            # Meaningful Name Fix: If they have low frustration and low boredom,
            # they didn't play long enough. They are just highly impatient players.
            if c_frust < 12 and c_bored < 12: 
                name = "Early Abandoners"
                dominant_emotion = "Low Patience"
            elif c_frust > c_bored: 
                name = "Rage Quitters"
            else: 
                name = "Bored Dropouts"

        if name in used_names:
            used_names[name] += 1
            final_name = f"{name} (Tier {used_names[name]})"
        else:
            used_names[name] = 1
            final_name = name
            
        archetypes.append({
            "name": final_name,
            "population": count,
            "avg_skill": round(c_skill, 1),
            "dominant_emotion": dominant_emotion
        })
        
    archetypes.sort(key=lambda x: x['population'], reverse=True)
    return archetypes