import numpy as np
import math

class Player:
    def __init__(self, p_id, start_difficulty):
        self.id = p_id
        self.skill = np.random.normal(start_difficulty, 5) 
        self.learning_rate = np.random.uniform(0.1, 1.5)
        self.frustration_rate = np.random.uniform(0.5, 2.0)
        self.reward_sensitivity = np.random.uniform(0.5, 2.0)
        self.quit_threshold = np.random.normal(15, 5)
        self.frustration = 0
        self.boredom = 0
        self.is_active = True
        self.day_quit = 30
        self.quit_reason = "Survived"
        self.history = []

    def update_state(self, system_config, day):
        if not self.is_active: return
        
        e_level = system_config['difficulty'] + (day * system_config['difficulty_growth'])
        reward_val = system_config['reward_amount']
        penalty = system_config['penalty_on_failure']
        level_gap = e_level - self.skill
        success = (self.skill + np.random.normal(0, 5)) >= e_level

        if level_gap < -15:
            self.boredom += 0.5 * self.frustration_rate
            self.frustration = max(0, self.frustration - 1)
        elif -15 <= level_gap <= 5:
            self.boredom = max(0, self.boredom - 1)
            self.frustration = max(0, self.frustration - (reward_val * self.reward_sensitivity / 15))
        else:
            self.frustration += (level_gap / 15) * self.frustration_rate * penalty
            self.boredom = max(0, self.boredom - 0.5)

        if success:
            self.skill += self.learning_rate
            
        self.history.append([self.skill, level_gap, self.frustration, self.boredom])

        if np.random.random() < 0.003: 
            self.is_active = False
            self.day_quit = day
            self.quit_reason = "Personal"
            return
            
        driver = max(self.frustration, self.boredom)
        prob = 1 / (1 + math.exp(-0.4 * (driver - self.quit_threshold)))
        
        if np.random.random() < prob:
            self.is_active = False
            self.day_quit = day
            self.quit_reason = "Frustration" if self.frustration > self.boredom else "Boredom"