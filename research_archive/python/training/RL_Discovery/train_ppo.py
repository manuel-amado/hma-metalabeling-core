import pandas as pd
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
import os
import torch
import warnings
warnings.filterwarnings('ignore')

class AlphaTradingEnv(gym.Env):
    def __init__(self, df, window_size=20, spread_penalty=0.15):
        super(AlphaTradingEnv, self).__init__()
        
        self.df = df.reset_index(drop=True)
        self.window_size = window_size
        self.spread_penalty = spread_penalty # In ATR units
        
        # Features to expose to the agent
        self.features = ['Slope10', 'Slope21', 'Slope50', 'Slope100', 'Slope200', 'RibbonSpread', 
                         'RibbonAlign', 'DistH4', 'DistD1', 'CandleVel', 'CandleDom', 'ZScore', 'RSI']
        
        self.action_space = spaces.Discrete(3) # 0: Flat, 1: Long, 2: Short
        self.observation_space = spaces.Box(
            low=-100, high=100, shape=(self.window_size, len(self.features)), dtype=np.float32
        )
        
        self.current_step = self.window_size
        self.position = 0 # 0: Flat, 1: Long, -1: Short
        self.net_worth = 0.0
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Start at a random point in the first 80% of data if training
        self.current_step = self.window_size + np.random.randint(0, len(self.df) - 50000)
        self.position = 0
        self.net_worth = 0.0
        return self._get_obs(), {}
        
    def _get_obs(self):
        obs = self.df[self.features].iloc[self.current_step - self.window_size : self.current_step].values
        # NaN handling just in case
        obs = np.nan_to_num(obs, nan=0.0)
        return obs.astype(np.float32)
        
    def step(self, action):
        # Map action 0, 1, 2 to position 0, 1, -1
        target_position = 0
        if action == 1: target_position = 1
        elif action == 2: target_position = -1
        
        reward = 0.0
        trade_penalty = 0.0
        
        # Calculate penalty for crossing spread
        if target_position != self.position:
            if self.position != 0 and target_position != 0:
                trade_penalty = self.spread_penalty * 2 # Close and open reverse
            else:
                trade_penalty = self.spread_penalty # Open or close
                
        self.position = target_position
        
        # Calculate Reward based on the next candle's movement
        if self.current_step < len(self.df) - 1:
            close_now = self.df['Close'].iloc[self.current_step]
            close_next = self.df['Close'].iloc[self.current_step + 1]
            atr = self.df['ATR14'].iloc[self.current_step]
            
            step_return = 0.0
            if self.position == 1:
                step_return = (close_next - close_now) / atr
            elif self.position == -1:
                step_return = (close_now - close_next) / atr
                
            reward = step_return - trade_penalty
            self.net_worth += reward
        
        self.current_step += 1
        
        # Done if we reach the end of the episode (max 1000 steps per episode to help gradient flow)
        terminated = False
        truncated = False
        
        # Arbitrary episode length to learn episodic returns
        if self.current_step % 2000 == 0 or self.current_step >= len(self.df) - 1:
            terminated = True
            
        # Small penalty for doing absolutely nothing forever to prevent local optima
        if self.position == 0:
            reward -= 0.001
            
        return self._get_obs(), float(reward), terminated, truncated, {}

def make_env(df, seed=0):
    def _init():
        env = AlphaTradingEnv(df)
        env.reset(seed=seed)
        return env
    return _init

if __name__ == '__main__':
    print("Loading Data...")
    df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_OHLC_Dump_XAUUSD.csv")
    df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')
    df = df.sort_values('Time').reset_index(drop=True)

    print("Building Features...")
    df['Slope10'] = (df['HMA10'] - df['HMA10'].shift(1)) / df['ATR14']
    df['Slope21'] = (df['HMA21'] - df['HMA21'].shift(1)) / df['ATR14']
    df['Slope50'] = (df['HMA50'] - df['HMA50'].shift(1)) / df['ATR14']
    df['Slope100'] = (df['HMA100'] - df['HMA100'].shift(1)) / df['ATR14']
    df['Slope200'] = (df['HMA200'] - df['HMA200'].shift(1)) / df['ATR14']

    mean_hma = (df['HMA10'] + df['HMA21'] + df['HMA50'] + df['HMA100'] + df['HMA200']) / 5.0
    sum_sq = (df['HMA10']-mean_hma)**2 + (df['HMA21']-mean_hma)**2 + (df['HMA50']-mean_hma)**2 + (df['HMA100']-mean_hma)**2 + (df['HMA200']-mean_hma)**2
    df['RibbonSpread'] = np.sqrt(sum_sq / 5.0) / df['ATR14']

    cond_align_1 = (df['HMA10'] > df['HMA21']) & (df['HMA21'] > df['HMA50']) & (df['HMA50'] > df['HMA100']) & (df['HMA100'] > df['HMA200'])
    cond_align_neg1 = (df['HMA10'] < df['HMA21']) & (df['HMA21'] < df['HMA50']) & (df['HMA50'] < df['HMA100']) & (df['HMA100'] < df['HMA200'])
    df['RibbonAlign'] = np.where(cond_align_1, 1, np.where(cond_align_neg1, -1, 0))

    df['DistH4'] = (df['Close'] - df['EMAH4']) / df['ATR14']
    df['DistD1'] = (df['Close'] - df['EMAD1']) / df['ATR14']

    df['CandleVel'] = (df['Close'] - df['Open']) / df['ATR14']
    cdl_range = df['High'] - df['Low']
    df['CandleDom'] = np.where(cdl_range > 0, (df['Close'] - df['Open']) / cdl_range, 0)
    df['ZScore'] = np.where(df['Close'].rolling(20).std() > 0, (df['Close'] - df['Close'].rolling(20).mean()) / df['Close'].rolling(20).std(), 0)

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + gain/loss))

    # Drop NaNs
    df = df.dropna().reset_index(drop=True)
    
    # Split into train (2015-2024) and eval (2025-2026)
    train_df = df[df['Time'].dt.year <= 2024].copy()
    
    print(f"Starting Multi-Core PPO Training on {len(train_df)} candles (2015-2024)...")
    
    # Use 8 cores for environment rollouts
    num_envs = 8
    env = SubprocVecEnv([make_env(train_df, i) for i in range(num_envs)])
    
    # Ensure torch uses the GPU if available, or fall back to fast CPU operations
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Training on Device: {device}")
    
    # Create PPO Agent
    policy_kwargs = dict(net_arch=[dict(pi=[128, 128], vf=[128, 128])])
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003, n_steps=2048, batch_size=256, 
                n_epochs=10, gamma=0.99, gae_lambda=0.95, clip_range=0.2, 
                policy_kwargs=policy_kwargs, device=device)
    
    out_dir = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\training\RL_Discovery"
    os.makedirs(out_dir, exist_ok=True)
    
    # Train for 1 Million Timesteps initially
    print("Beginning Training...")
    model.learn(total_timesteps=1000000, progress_bar=False)
    
    model.save(os.path.join(out_dir, "ppo_alpha_omni_v1"))
    print("Training Complete. Model Saved.")
