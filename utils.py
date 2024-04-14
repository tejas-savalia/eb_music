import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import ast, os
import bambi as bmb
import pymc as pm
import arviz as az
import scipy.stats as stat
from collections import Counter
import itertools


def clean_data(filename, type = 'exposure'):
    # print(filename)
    # Handle errors. If there is an error, go to 'except' and return nothing.
    data = pd.read_csv('data/' + filename)
    
    if type == 'exposure':
        try:
    
            # Drop instruction rows by dropping rows with missing data in column: 'blocks.thisRepN'
            data = data.dropna(subset=['blocks.thisRepN']).reset_index(drop=True)
    
            #If data file is incomplete, raise an error. 
            if sum(data['node idx'].notna()) < 1400:
                raise TypeError('Incomplete Data')
    
    
            #Rt is average rt of all keys pressed
            data['rt'] = [np.mean(ast.literal_eval(data['key_resp.rt'][i])) if data['accuracy'][i] else np.NaN for i in range(len(data))]
            
            #Transition type is cross cluster if goes from boundary to boundary
            data['transition_type'] = ['cross cluster' if (data['node type'] == 'boundary')[i] & (data['node type'].shift() == 'boundary')[i] else 'within cluster' for i in range(len(data))]
    
            #Label conditions based on participant number as was designed in the experiment
            if data['participant'][0]%3 == 0:
                data['condition'] = 'random'
            elif data['participant'][0]%3 == 1:
                data['condition'] = 'music random'
            else:
                data['condition'] = 'structured'
    
            data['trial'] = np.arange(len(data))
            return data[['participant', 'trial', 'blocks.thisRepN', 'accuracy', 'condition', 'node type', 'transition_type', 'rt', 'stim']]
        except:
            return None
    else:
        try:
            mem_data = data.loc[data['mem test stim'].notna(), ['mem test stim', 'mem test resp']].reset_index(drop=True)
            mem_data.rename(columns={'mem test stim': 'stim'}, inplace=True)
            
            music_stim = []
            corr_key_resp = []
            node_id = []
            stim_key_map = {}
            for ms in data['selected music stim'].unique():
                if ms is np.NaN:
                    continue
                music_stim.append(ms[16:])
                corr_key_resp.append(data.loc[data['selected music stim'] == ms, 'stim'].unique()[0])    
                stim_key_map[ms[16:]] = data.loc[data['selected music stim'] == ms, 'stim'].unique()
                node_id.append(data.loc[data['selected music stim'] == ms, 'node type'].unique()[0])    
            
            stim_key_df = pd.DataFrame({'stim': music_stim, 
                                        'corr key resp': corr_key_resp,
                                        'node type': node_id
                                       })
            
            
            memory = mem_data.merge(stim_key_df, on=['stim'])
            memory['accuracy'] = [ast.literal_eval(memory['corr key resp'][i]) == tuple(ast.literal_eval(memory['mem test resp'][i])) for i in range(len(memory))]
            memory['participant'] = data['participant'][0]
    
            if memory['participant'][0]%3 == 0:
                memory['condition'] = 'random'
            elif memory['participant'][0]%3 == 1:
                memory['condition'] = 'music random'
            else:
                memory['condition'] = 'structured'
    
            return memory
        except:
            return None
    # except:
    #     return None

    # #Count the number of keys to be pressed for each stimuli
    # data['num_keypress'] = [len(ast.literal_eval(data['stim'][i])) for i in range(len(data))]


    
    # #Return the dataframe with relevant columns
    # if type == 'exposure:
