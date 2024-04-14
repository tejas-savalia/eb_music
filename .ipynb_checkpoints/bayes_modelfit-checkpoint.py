# Import the required packages

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
from utils import *

data_files = []
for f in os.listdir('data/'):
    if (f.startswith('240') & f.endswith('csv')):
        data_files.append(f)


df_clean = pd.concat([clean_data(f) for f in data_files]).reset_index(drop = True)
df_clean_memory = pd.concat([clean_data(f, 'memory') for f in data_files]).reset_index(drop = True)

# df_clean['reset'] = 'False'
# df_clean.loc[df_clean['trial'].values%(df_clean['walk_length'].values+1) == 0, 'reset'] = 'True'



df_clean_rt_outlier = df_clean[np.abs(stat.zscore(df_clean['rt'], nan_policy='omit')) < 3]
df_clean_rt_outlier['node_transition_type'] = df_clean_rt_outlier['node type']+'_'+df_clean_rt_outlier['transition_type']

model = bmb.Model('rt ~ condition + (node_transition_type|participant) + (blocks.thisRepN|participant)', data = df_clean_rt_outlier)
model.build()
samples = model.fit(idata_kwargs={"log_likelihood": True})
samples.to_netcdf('hrl_nttp_blockp.nc')

