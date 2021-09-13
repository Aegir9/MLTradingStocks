# -*- coding: utf-8 -*-
"""Implementação - Adam King.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/167fi6dpyxccDH5E4Q1D4zOop3YR-vK4o
"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 2.x
! pip install tensorflow
!pip install stable-baselines3 gym
!pip install torch==1.4.0

import gym
from gym import spaces
import random
import numpy as np
import pandas as pd



from stable_baselines3.sac.policies import MlpPolicy
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import PPO

qtd_episodios = 0
episodios = []

INITIAL_ACCOUNT_BALANCE = 1000.00
MAX_ACCOUNT_BALANCE = 200000.00
MAX_NUM_SHARES = 100000
MAX_SHARE_PRICE = 100000.00
MAX_STEPS = 20000


class StockTradingEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, df):
        super(StockTradingEnvironment, self).__init__()
        self.df = df
        self.reward_range = (0, MAX_ACCOUNT_BALANCE)

        # Actions of the format Buy x%, Sell x%, Hold, etc. - NÃO ENTENDI O VETOR DE ACTION_SPACE - Buy, sell, hold; 0-100% account balance/position size
        self.action_space = spaces.Box(
            low=np.array([0, 0]),
            high=np.array([3, 1]),
            dtype=np.float16)

        # Prices contain the OHCL values for the last five prices - NÃO ENTENDI O VETOR DE OBSERVATION_SPACE - O QUE É O SHAPE? - MATRIZ
        self.observation_space = spaces.Box(
            low=0,
            high=1,
            shape=(6, 6),
            dtype=np.float16)

    def reset(self):
        # Reset the state of the environment to an initial state
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.net_worth = INITIAL_ACCOUNT_BALANCE
        self.max_net_worth = INITIAL_ACCOUNT_BALANCE
        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.share_price = 0
        

        # Set the current step to a random point within the dataframe
        # self.current_step = random.randint(0, len(self.df.loc[:, 'Open'].values) - 6)
        self.current_step = random.randint(5, len(self.df)-1)

        return self._next_observation()


    def _next_observation(self):
        # Get the data points for the last 5 days and scale to between 0-1 - POR QUE DE 0 A 1? - SÃO OS 5 ÚLTIMOS DIAS OU OS 5 DIAS À FRENTE???
        frame = np.array([
            self.df.loc[self.current_step - 5: self.current_step, 'Open'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step - 5: self.current_step, 'High'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step - 5: self.current_step, 'Low'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step - 5: self.current_step, 'Close'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step - 5: self.current_step, 'Volume'].values / MAX_SHARE_PRICE,
        ])
        # print(self.current_step)
        # print(frame)

        # Cotação Mais Atual
        self.share_price = self.df.loc[self.current_step: self.current_step, 'Close']
        

        # Append additional data and scale each value to between 0-1 - POR QUE DE 0 A 1?
        obs = np.append(frame, [[
            self.balance / MAX_ACCOUNT_BALANCE,
            self.max_net_worth / MAX_ACCOUNT_BALANCE,
            self.shares_held / MAX_NUM_SHARES,
            self.cost_basis / MAX_SHARE_PRICE,
            self.total_shares_sold / MAX_NUM_SHARES,
            self.total_sales_value / (MAX_NUM_SHARES * MAX_SHARE_PRICE),
        ]], axis=0)

        # print('Depois do append')
        # print(obs)
        

        return obs

    def step(self, action):
        
        # Execute one time step within the environment
        self._take_action(action)

        # Increase step number
        self.current_step += 1

        if self.current_step > len(self.df) - 1:
            self.current_step = 5

        delay_modifier = (self.current_step / MAX_STEPS)

        reward = self.balance * delay_modifier
        done = self.net_worth <= 0

        if done:
          qtd_episodios += 1
          episodios.append([self.current_step, qtd_episodios])

        obs = self._next_observation()
        # Mudar obs pra next_stage

        return obs, reward, done, {}

    def _take_action(self, action):
        # Set the current price to a random price within the time step
        current_price = random.uniform(
            self.df.loc[self.current_step, 'Open'],
            self.df.loc[self.current_step, 'Close'])

        action_type = action[0]
        amount = action[1]

        print(f'Action Type: {action_type}\nAmount: {amount}')
        if action_type < 1:
            # Buy amount % of balance in shares
            total_possible = int(self.balance / current_price)
            shares_bought = int(total_possible * amount)
            prev_cost = self.cost_basis * self.shares_held
            additional_cost = shares_bought * current_price

            self.balance -= additional_cost
            self.cost_basis = (prev_cost + additional_cost) / (self.shares_held + shares_bought)
            self.shares_held += shares_bought

        elif action_type < 2:
            # Sell amount % of shares held
            shares_sold = int(self.shares_held * amount)
            self.balance += shares_sold * current_price
            self.shares_held -= shares_sold
            self.total_shares_sold += shares_sold
            self.total_sales_value += shares_sold * current_price

        self.net_worth = self.balance + self.shares_held * current_price

        if self.net_worth > self.max_net_worth:
            self.max_net_worth = self.net_worth

        if self.shares_held == 0:
            self.cost_basis = 0
        

    def render(self, mode='human', close=False):
        # Render the environment to the screen
        profit = self.net_worth - INITIAL_ACCOUNT_BALANCE

        print()
        print(f'Step: {self.current_step}')
        print(f'Balance: {self.balance}')
        print(f'Shares held: {self.shares_held}\nTotal Sold: {self.total_shares_sold}')
        print(f'Share price: {self.share_price}')
        print(f'Average cost for held shares: {self.cost_basis}\nTotal sales value: {self.total_sales_value}')
        print(f'Net worth: {self.net_worth}\nMax net worth: {self.max_net_worth}')
        print(f'Profit: {profit}')




outer_df = pd.read_csv('AAPL Before Training.csv')
outer_df = outer_df.sort_values('Date')
# print(outer_df.head())

after_training_df = pd.read_csv('AAPL After Training Adjusted.csv')
after_training_df = after_training_df.sort_values('Date')

# The algorithms require a vectorized environment to run
env = DummyVecEnv([lambda: StockTradingEnvironment(outer_df)])

env_after = DummyVecEnv([lambda: StockTradingEnvironment(after_training_df)])


# Criar env de teste
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=1000)

model.save('teste')

model_after_training = PPO("MlpPolicy", env_after, verbose=1)

print()
print(episodios)

# https://stable-baselines3.readthedocs.io/en/master/guide/examples.html

env_test = DummyVecEnv([lambda: StockTradingEnvironment(after_training_df)])

obs = env_test.reset()

# Evaluate the agent
rewards = []
episode_reward = 0
for _ in range(1000):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, info = env_test.step(action)
    episode_reward += reward
    if done or info[0].get('is_success', False):
        print("Reward:", episode_reward, "Success?", info[0].get('is_success', False))
        rewards.append(episode_reward)
        episode_reward = 0.0
        obs = env.reset()

print(rewards)

obs = env.reset()
obs2 = env_after.reset()
# Episodes
for _ in range(10000):
    action, _states = model.predict(obs2)
    # Ajustar, para rodar sobre base de dados nova

    obs, rewards, done, info = env.step(action)
    env.render()