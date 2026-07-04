from sumo_rl import parallel_env
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
import numpy as np
import random
import os

# Define the environment using PettingZoo API
train_env = parallel_env(
    net_file='2024-07-18-02-25-27/osm2.net.xml',
    route_file='2024-07-18-02-25-27/never_ending.rou.xml',
    out_csv_name='outputs/train2_dqn',
    use_gui=False,
    num_seconds=1000,
    min_green=10,
    delta_time=5,
    yellow_time=3,
    single_agent=False,
    max_green=180,
)


# Determine the maximum state size
max_state_size = max(train_env.observation_spaces[agent_id].shape[0] for agent_id in train_env.possible_agents)

class DQNAgent:
    def __init__(self, state_size, action_size, max_state_size):
        self.state_size = state_size
        self.action_size = action_size
        self.max_state_size = max_state_size
        self.memory = []
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.01
        self.model = self._build_model()
        self.save_dir = 'models/train 1/'  # Directory to save the model files

    def _build_model(self):
        model = Sequential()
        model.add(Input(shape=(self.max_state_size,)))
        model.add(Dense(40, activation='relu'))
        model.add(Dense(40, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate))
        return model

    def pad_and_reshape(self, state):
        padded_state = np.pad(state, (0, self.max_state_size - len(state)), 'constant')
        return np.reshape(padded_state, (1, self.max_state_size))

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        state = self.pad_and_reshape(state)
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])

    def replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        states = np.array([self.pad_and_reshape(exp[0]) for exp in minibatch])
        actions = np.array([exp[1] for exp in minibatch])
        rewards = np.array([exp[2] for exp in minibatch])
        next_states = np.array([self.pad_and_reshape(exp[3]) for exp in minibatch])
        dones = np.array([exp[4] for exp in minibatch])

        states = states.squeeze(axis=1)  # Remove the unnecessary dimension
        next_states = next_states.squeeze(axis=1)  # Remove the unnecessary dimension

        # Predict target Q-values
        targets = rewards + self.gamma * np.amax(self.model.predict(next_states), axis=1) * (1 - dones)
        targets_full = self.model.predict(states,)
        indices = np.arange(batch_size)
        targets_full[indices, actions] = targets

        # Train the model
        self.model.fit(states, targets_full, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
    def save_model(self, episode, agent_id):
        # Save the model
        model_path = os.path.join(self.save_dir, f"agent_{agent_id}_model2_episode_{episode}.h5")
        self.model.save(model_path)
        

def get_avg_waiting_time(env):
    junction_waiting_times = {agent_id: 0 for agent_id in env.possible_agents}
    for vehicle_id in env.vehicle.getIDList():
        wait_time = env.vehicle.getWaitingTime(vehicle_id)
        junction_id = env.vehicle.getRoadID(vehicle_id)
        if junction_id in junction_waiting_times:
            junction_waiting_times[junction_id] += wait_time
    avg_waiting_times = {agent_id: junction_waiting_times[agent_id] / max(len(traci.vehicle.getIDList()), 1) for agent_id in env.possible_agents}
    return avg_waiting_times


        
    # def load_agent_models(agents, model_directory):
    #     for agent_id, agent in agents.items():
    #         model_path = os.path.join(model_directory, f"agent_{agent_id}_model_episode_1.h5")  # Adjust the episode number as needed
    #         agent.load_model(model_path)
    #         agent.epsilon = 0  # Disable exploration for testing

# Initialize agents
agents = {}
for agent_id in train_env.possible_agents:
    state_size = train_env.observation_spaces[agent_id].shape[0]
    action_size = train_env.action_spaces[agent_id].n
    agents[agent_id] = DQNAgent(state_size, action_size, max_state_size)
    print(f"Agent {agent_id}, Action State: {train_env.action_spaces[agent_id]}")

def train_agents(env, agents):
    EPISODES = 100
    
    previous_avg_waiting_times = get_avg_waiting_time(env)
    
    for e in range(EPISODES):
        observations = env.reset()
        if isinstance(observations, tuple):
            observations_dict = observations[0]
        else:
            observations_dict = observations

        total_rewards = {agent_id: 0 for agent_id in agents}
        
        while env.agents:
            actions = {}
            for agent_id, agent in agents.items():
                state_agent = observations_dict[agent_id]
                action = agent.act(state_agent)
                actions[agent_id] = action
            
            next_observations, rewards, terminations, truncations, infos = env.step(actions)
            
            if isinstance(next_observations, tuple):
                next_observations_dict = next_observations[0]
            else:
                next_observations_dict = next_observations
            
            current_avg_waiting_times = get_avg_waiting_time(env)
            
            for agent_id, agent in agents.items():
                next_state_agent = next_observations_dict[agent_id]
                delta_waiting_time = previous_avg_waiting_times[agent_id] - current_avg_waiting_times[agent_id]
                
                # Assign rewards based on the change in average waiting time
                rewards[agent_id] = delta_waiting_time

                agent.remember(state_agent, actions[agent_id], rewards[agent_id], next_state_agent, terminations[agent_id])
                total_rewards[agent_id] += rewards[agent_id]
            
            observations = next_observations_dict
            previous_avg_waiting_times = current_avg_waiting_times

            for agent_id, agent in agents.items():
                agent.replay(32)
                
        # After completing the episode:
        for agent_id, agent in agents.items():
            agent.save_model(e, agent_id)  # Save each agent's model after each episode

        print(f"Episode: {e}/{EPISODES}, Rewards: {total_rewards}")

    env.close()

    
test_env = parallel_env(
    net_file='2024-07-18-02-25-27/osm2.net.xml',
    route_file='2024-07-18-02-25-27/test_route.rou.xml',
    out_csv_name='outputs/output_test_dqn',
    use_gui=True,
    num_seconds=1000,
    min_green=10,
    max_green=180,
    delta_time=5,
    yellow_time=3,
)

def load_agent_models(agents, model_directory):
    for agent_id, agent in agents.items():
        model_path =f"models/train 1/agent_{agent_id}_model2_episode_1.h5"  # Adjust the episode number as needed
        agent.model.load_weights(model_path)
        agent.epsilon = 0  # Disable exploration for testing

    
def test_agents(env, agents, episodes=10, model_directory='models/train_2'):
    load_agent_models(agents, model_directory)

    total_test_rewards = {agent_id: 0 for agent_id in agents}
    for _ in range(episodes):
        observations = env.reset()
        if isinstance(observations, tuple):
            observations_dict = observations[0]
        else:
            observations_dict = observations

        while env.agents:
            actions = {}
            for agent_id, agent in agents.items():
                state_agent = observations_dict[agent_id]
                action = agent.act(state_agent)
                actions[agent_id] = action

            next_observations, rewards, terminations, truncations, infos = env.step(actions)
            if isinstance(next_observations, tuple):
                next_observations_dict = next_observations[0]
            else:
                next_observations_dict = next_observations
            
            for agent_id in agents:
                total_test_rewards[agent_id] += rewards[agent_id]
            
            observations = next_observations_dict
    
    avg_test_rewards = {agent_id: total_test_rewards[agent_id] / episodes for agent_id in agents}
    print(f"Average Test Rewards: {avg_test_rewards}")

    
    

# Example usage

# test_agents(test_env, agents)

train_agents(train_env, agents)


