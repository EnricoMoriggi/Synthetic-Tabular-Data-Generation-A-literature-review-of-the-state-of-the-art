# -*- coding: utf-8 -*-
"""TesiFRAUD.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gwoUT3GcZmmEUH6fvo0xw_lIMXOQo5WZ
"""

import pandas as pd

from google.colab import drive
drive.mount('/content/drive')

df = pd.read_csv('/content/drive/My Drive/increased_transaction_dataset.csv')

df.info()

df = df.drop(df.columns[[0, 15,16,17,18,19]], axis=1)

df.info()

df['FLAG']=df['FLAG'].replace({'Non - Fraud':0, 'Fraud':1}).astype(float)
df['Sent tnx']=df['Sent tnx'].astype(float)
df['Received Tnx']=df['Received Tnx'].astype(float)
df['Number of Created Contracts']=df['Number of Created Contracts'].astype(float)

df.isnull().sum()

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.figure(figsize=(8, 6))
cor = round(df.corr(), 3)
sns.heatmap(cor, cmap='viridis', annot=True, annot_kws={"size": 8}, linewidths=0.5, linecolor='white')
plt.title('Correlation')
plt.show()

pip install ctgan

from ctgan import CTGAN
ctgan = CTGAN()
ctgan.fit(df)

df_CTGAN = ctgan.sample(19682)
print(df_CTGAN.head(10))

df_CTGAN['FLAG']=df_CTGAN['FLAG'].round().abs()
df_CTGAN['Sent tnx']=df_CTGAN['Sent tnx'].round().abs()
df_CTGAN['Received Tnx']=df_CTGAN['Received Tnx'].round().abs()
df_CTGAN['Number of Created Contracts']=df_CTGAN['Number of Created Contracts'].round().abs()

print(df_CTGAN.head(10))

from scipy.stats import ks_2samp

for col in df.columns:
    statistic, p_value = ks_2samp(df[col], df_CTGAN[col])
    print(f"{col}: KS statistic = {statistic}, p-value = {p_value.round(3)}")

import seaborn as sns
import matplotlib.pyplot as plt

columns = df.columns

plt.figure(figsize=(15, 10))

x_limits = {
    'FLAG': (-1, 2),
    'Avg min between sent tnx': (-20000, 50000),
    'Avg min between received tnx': (-20000, 50000),
    'Time Diff between first and last (Mins)': (-200000, 500000),
    'Sent tnx': (-1000, 1000),
    'Received Tnx': (-1000, 1000),
    'Number of Created Contracts': (-100, 100),
    'max value received': (-2000, 10000),
    'avg val received': (-2000, 5000),
    'avg val sent': (-500, 500),
    'total Ether sent': (-50000, 50000),
    'total ether balance': (-50000, 100000),
    'ERC20 total Ether received': (-5000, 5000),
    'ERC20 total ether sent': (-5000, 5000)
}

for i, col in enumerate(columns, 1):
    plt.subplot(3, 5, i)
    sns.kdeplot(df[col], label='Real', color='red')
    sns.kdeplot(df_CTGAN[col], label='Synthetic', color='blue')
    plt.title(f' {col}')
    plt.legend()


    if col in x_limits:
        plt.xlim(x_limits[col])

plt.tight_layout()
plt.show()

from ctgan import TVAE

tvae= TVAE()
tvae.fit(df)

df_TVAE= tvae.sample(19682)
print(df_TVAE.head(10))

df_TVAE['FLAG']=df_TVAE['FLAG'].round().abs()
df_TVAE['Sent tnx']=df_TVAE['Sent tnx'].round().abs()
df_TVAE['Received Tnx']=df_TVAE['Received Tnx'].round().abs()
df_TVAE['Number of Created Contracts']=df_TVAE['Number of Created Contracts'].round().abs()

print(df_TVAE.head(10))

import seaborn as sns
import matplotlib.pyplot as plt

columns = df.columns

plt.figure(figsize=(15, 10))

x_limits = {
    'FLAG': (-1, 2),
    'Avg min between sent tnx': (-20000, 50000),
    'Avg min between received tnx': (-20000, 50000),
    'Time Diff between first and last (Mins)': (-200000, 500000),
    'Sent tnx': (-1000, 1000),
    'Received Tnx': (-1000, 1000),
    'Number of Created Contracts': (-100, 100),
    'max value received': (-2000, 10000),
    'avg val received': (-2000, 5000),
    'avg val sent': (-500, 500),
    'total Ether sent': (-50000, 50000),
    'total ether balance': (-50000, 100000),
    'ERC20 total Ether received': (-5000, 5000),
    'ERC20 total ether sent': (-5000, 5000)
}

for i, col in enumerate(columns, 1):
    plt.subplot(3, 5, i)
    sns.kdeplot(df[col], label='Real', color='red')
    sns.kdeplot(df_TVAE[col], label='Synthetic', color='blue')
    plt.title(f' {col}')
    plt.legend()


    if col in x_limits:
        plt.xlim(x_limits[col])

plt.tight_layout()
plt.show()

import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader

data = df

scaler = MinMaxScaler(feature_range=(-1, 1))
data_scaled = scaler.fit_transform(data)

data_scaled_df = pd.DataFrame(data_scaled, columns=data.columns)


latent_dim = 100
data_dim = data_scaled_df.shape[1]
n_epochs = 100
batch_size = 64
lr = 0.0002


class TabularGenerator(nn.Module):
    def __init__(self):
        super(TabularGenerator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(128, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, data_dim),
            nn.Tanh()
        )

    def forward(self, z):
        return self.model(z)

class TabularDiscriminator(nn.Module):
    def __init__(self):
        super(TabularDiscriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(data_dim, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)


generator = TabularGenerator()
discriminator = TabularDiscriminator()


optimizer_G = torch.optim.Adam(generator.parameters(), lr=lr)
optimizer_D = torch.optim.Adam(discriminator.parameters(), lr=lr)


adversarial_loss = torch.nn.BCELoss()


data_tensor = torch.tensor(data_scaled_df.values, dtype=torch.float32)
dataloader = DataLoader(data_tensor, batch_size=batch_size, shuffle=True)

Tensor = torch.FloatTensor

for epoch in range(n_epochs):
    for i, real_data in enumerate(dataloader):
        valid = Variable(Tensor(real_data.size(0), 1).fill_(1.0), requires_grad=False)
        fake = Variable(Tensor(real_data.size(0), 1).fill_(0.0), requires_grad=False)

        optimizer_G.zero_grad()
        z = Variable(Tensor(np.random.normal(0, 1, (real_data.shape[0], latent_dim))))
        generated_data = generator(z)
        g_loss = adversarial_loss(discriminator(generated_data), valid)
        g_loss.backward()
        optimizer_G.step()

        optimizer_D.zero_grad()
        real_loss = adversarial_loss(discriminator(real_data), valid)
        fake_loss = adversarial_loss(discriminator(generated_data.detach()), fake)
        d_loss = (real_loss + fake_loss) / 2
        d_loss.backward()
        optimizer_D.step()

    print(f"[Epoch {epoch}/{n_epochs}] [D loss: {d_loss.item()}] [G loss: {g_loss.item()}]")


z = Variable(Tensor(np.random.normal(0, 1, (19682, latent_dim))))
samples = generator(z).detach().cpu().numpy()

samples_denorm = scaler.inverse_transform(samples)


df_GAN = pd.DataFrame(samples_denorm, columns=data.columns)
print(df_GAN.head())

df_GAN['FLAG']=df_GAN['FLAG'].round().abs()
df_GAN['Sent tnx']=df_GAN['Sent tnx'].round().abs()
df_GAN['Received Tnx']=df_GAN['Received Tnx'].round().abs()
df_GAN['Number of Created Contracts']=df_GAN['Number of Created Contracts'].round().abs()

print(df_GAN.head(10))

import seaborn as sns
import matplotlib.pyplot as plt

columns = df.columns

plt.figure(figsize=(15, 10))

x_limits = {
    'FLAG': (-1, 2),
    'Avg min between sent tnx': (-20000, 50000),
    'Avg min between received tnx': (-20000, 50000),
    'Time Diff between first and last (Mins)': (-200000, 2000000),
    'Sent tnx': (-1000, 1000),
    'Received Tnx': (-1000, 1000),
    'Number of Created Contracts': (-100, 100),
    'max value received': (-2000, 10000),
    'avg val received': (-2000, 5000),
    'avg val sent': (-500, 500),
    'total Ether sent': (-50000, 50000),
    'total ether balance': (-1000000, 1000000),
    'ERC20 total Ether received': (-50000, 50000),
    'ERC20 total ether sent': (-5000, 5000)
}

for i, col in enumerate(columns, 1):
    plt.subplot(3, 5, i)
    sns.kdeplot(df[col], label='Real', color='red')
    sns.kdeplot(df_GAN[col], label='Synthetic', color='blue')
    plt.title(f' {col}')
    plt.legend()


    if col in x_limits:
        plt.xlim(x_limits[col])

plt.tight_layout()
plt.show()

import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader

data = df

scaler = MinMaxScaler(feature_range=(-1, 1))
data_scaled = scaler.fit_transform(data)

data_scaled_df = pd.DataFrame(data_scaled, columns=data.columns)

latent_dim = 100
data_dim = data_scaled_df.shape[1]
n_epochs = 100
batch_size = 64
lr = 0.0002

class TabularGenerator(nn.Module):
    def __init__(self):
        super(TabularGenerator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(128, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, data_dim),
            nn.Tanh()
        )

    def forward(self, z):
        return self.model(z)


class TabularDiscriminator(nn.Module):
    def __init__(self):
        super(TabularDiscriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(data_dim, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)


generator = TabularGenerator()
discriminator = TabularDiscriminator()


optimizer_G = torch.optim.Adam(generator.parameters(), lr=lr)
optimizer_D = torch.optim.Adam(discriminator.parameters(), lr=lr)


adversarial_loss = torch.nn.BCELoss()


data_tensor = torch.tensor(data_scaled_df.values, dtype=torch.float32)
dataloader = DataLoader(data_tensor, batch_size=batch_size, shuffle=True)

Tensor = torch.FloatTensor


for epoch in range(n_epochs):
    for i, real_data in enumerate(dataloader):
        valid = Variable(Tensor(real_data.size(0), 1).fill_(1.0), requires_grad=False)
        fake = Variable(Tensor(real_data.size(0), 1).fill_(0.0), requires_grad=False)


        optimizer_G.zero_grad()
        z = Variable(Tensor(np.random.normal(0, 1, (real_data.shape[0], latent_dim))))
        generated_data = generator(z)
        g_loss = adversarial_loss(discriminator(generated_data), valid)
        g_loss.backward()
        optimizer_G.step()


        optimizer_D.zero_grad()
        real_loss = adversarial_loss(discriminator(real_data), valid)
        fake_loss = adversarial_loss(discriminator(generated_data.detach()), fake)
        d_loss = (real_loss + fake_loss) / 2
        d_loss.backward()
        optimizer_D.step()

    print(f"[Epoch {epoch}/{n_epochs}] [D loss: {d_loss.item()}] [G loss: {g_loss.item()}]")


z = Variable(Tensor(np.random.normal(0, 1, (19682, latent_dim))))
samples = generator(z).detach().cpu().numpy()

samples_denorm = scaler.inverse_transform(samples)


df_DCGAN = pd.DataFrame(samples_denorm, columns=data.columns)
print(df_DCGAN.head())

df_DCGAN['FLAG']=df_DCGAN['FLAG'].round().abs()
df_DCGAN['Sent tnx']=df_DCGAN['Sent tnx'].round().abs()
df_DCGAN['Received Tnx']=df_DCGAN['Received Tnx'].round().abs()
df_DCGAN['Number of Created Contracts']=df_DCGAN['Number of Created Contracts'].round().abs()

print(df_DCGAN.head(10))

import seaborn as sns
import matplotlib.pyplot as plt

columns = df.columns

plt.figure(figsize=(15, 10))

x_limits = {
    'FLAG': (-1, 2),
    'Avg min between sent tnx': (-20000, 50000),
    'Avg min between received tnx': (-20000, 50000),
    'Time Diff between first and last (Mins)': (-200000, 2000000),
    'Sent tnx': (-1000, 1000),
    'Received Tnx': (-1000, 1000),
    'Number of Created Contracts': (-100, 100),
    'max value received': (-2000, 10000),
    'avg val received': (-2000, 5000),
    'avg val sent': (-500, 500),
    'total Ether sent': (-100000, 200000),
    'total ether balance': (-1000000, 200000),
    'ERC20 total Ether received': (-50000, 50000),
    'ERC20 total ether sent': (-5000, 5000)
}

for i, col in enumerate(columns, 1):
    plt.subplot(3, 5, i)
    sns.kdeplot(df[col], label='Real', color='red')
    sns.kdeplot(df_DCGAN[col], label='Synthetic', color='blue')
    plt.title(f' {col}')
    plt.legend()


    if col in x_limits:
        plt.xlim(x_limits[col])

plt.tight_layout()
plt.show()

import numpy as np
import torch
from torch.nn import Linear, Module, ReLU
from torch.optim import Adam
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

data = df

scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)
data_tensor = torch.tensor(data_scaled, dtype=torch.float32)

dataset = TensorDataset(data_tensor)
loader = DataLoader(dataset, batch_size=500, shuffle=True)

class Encoder(Module):
    def __init__(self, input_dim, compress_dims, embedding_dim):
        super(Encoder, self).__init__()
        layers = []
        dim = input_dim
        for item in compress_dims:
            layers.append(Linear(dim, item))
            layers.append(ReLU())
            dim = item
        self.compress = torch.nn.Sequential(*layers)
        self.fc_mu = Linear(dim, embedding_dim)
        self.fc_var = Linear(dim, embedding_dim)

    def forward(self, x):
        x = self.compress(x)
        return self.fc_mu(x), torch.exp(0.5 * self.fc_var(x))

class Decoder(Module):
    def __init__(self, embedding_dim, decompress_dims, output_dim):
        super(Decoder, self).__init__()
        layers = []
        dim = embedding_dim
        for item in decompress_dims:
            layers.append(Linear(dim, item))
            layers.append(ReLU())
            dim = item
        layers.append(Linear(dim, output_dim))
        self.decompress = torch.nn.Sequential(*layers)

    def forward(self, x):
        return self.decompress(x)

class VAE(Module):
    def __init__(self, input_dim, compress_dims, decompress_dims, embedding_dim):
        super(VAE, self).__init__()
        self.encoder = Encoder(input_dim, compress_dims, embedding_dim)
        self.decoder = Decoder(embedding_dim, decompress_dims, input_dim)

    def forward(self, x):
        mu, std = self.encoder(x)
        eps = torch.randn_like(std)
        z = mu + std * eps
        return self.decoder(z), mu, std

def loss_function(recon_x, x, mu, logvar):
    BCE = torch.nn.functional.mse_loss(recon_x, x, reduction='sum')  # Mean squared error per dati continui
    KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())  # Kullback-Leibler Divergence
    return BCE + KLD

input_dim = data_tensor.shape[1]
embedding_dim = 128
compress_dims = [128, 128]
decompress_dims = [128, 128]
vae = VAE(input_dim, compress_dims, decompress_dims, embedding_dim)

optimizer = Adam(vae.parameters(), lr=1e-3)

epochs = 200
vae.train()
for epoch in range(epochs):
    for batch_idx, (data,) in enumerate(loader):
        optimizer.zero_grad()
        recon_batch, mu, logvar = vae(data)
        loss = loss_function(recon_batch, data, mu, logvar)
        loss.backward()
        optimizer.step()
    print(f'Epoch {epoch+1}/{epochs}, Loss: {loss.item()}')

vae.eval()
with torch.no_grad():
    z = torch.randn(19682, embedding_dim)
    samples = vae.decoder(z).cpu().numpy()

samples_denorm= scaler.inverse_transform(samples)
df_VAE = pd.DataFrame(samples_denorm)

print(df_VAE.head())

df_VAE = df_VAE.rename(columns={ 0 :  'FLAG',
 1 :  'Avg min between sent tnx',
 2  : 'Avg min between received tnx',
 3  : 'Time Diff between first and last (Mins)',
 4  : 'Sent tnx',
 5  : 'Received Tnx',
 6  : 'Number of Created Contracts',
 7  : 'max value received ',
 8  : 'avg val received',
 9  : 'avg val sent',
 10 : 'total Ether sent',
 11 : 'total ether balance',
 12 :  ' ERC20 total Ether received',
 13 :  ' ERC20 total ether sent'})

df_VAE['FLAG']=df_VAE['FLAG'].round().abs()
df_VAE['Sent tnx']=df_VAE['Sent tnx'].round().abs()
df_VAE['Received Tnx']=df_VAE['Received Tnx'].round().abs()
df_VAE['Number of Created Contracts']=df_VAE['Number of Created Contracts'].round().abs()

print(df_VAE.head(10))

df_VAE.columns

df.columns

import seaborn as sns
import matplotlib.pyplot as plt

columns = df.columns

plt.figure(figsize=(15, 10))

x_limits = {
    'FLAG': (-1, 2),
    'Avg min between sent tnx': (-20000, 50000),
    'Avg min between received tnx': (-20000, 50000),
    'Time Diff between first and last (Mins)': (-200000, 2000000),
    'Sent tnx': (-1000, 1000),
    'Received Tnx': (-1000, 1000),
    'Number of Created Contracts': (-100, 100),
    'max value received': (-2000, 10000),
    'avg val received': (-2000, 5000),
    'avg val sent': (-500, 500),
    'total Ether sent': (-1000000, 2000000),
    'total ether balance': (-1000000, 1000000),
    'ERC20 total Ether received': (-50000, 50000),
    'ERC20 total ether sent': (-5000, 5000)
}

for i, col in enumerate(columns, 1):
    plt.subplot(3, 5, i)
    sns.kdeplot(df[col], label='Real', color='red')
    sns.kdeplot(df_VAE[col], label='Synthetic', color='blue')
    plt.title(f' {col}')
    plt.legend()


    if col in x_limits:
        plt.xlim(x_limits[col])

plt.tight_layout()
plt.show()

import numpy as np

from sklearn.neighbors import KernelDensity
from sklearn.preprocessing import MinMaxScaler

data=df

scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

kde = KernelDensity(kernel='gaussian', bandwidth=0.5)
kde.fit(data_scaled)

samples = kde.sample(19682)
samples_denorm = scaler.inverse_transform(samples)
df_KDE = pd.DataFrame(samples_denorm, columns=data.columns)

print(df_KDE.head())

df_KDE['FLAG']=df_KDE['FLAG'].round().abs()
df_KDE['Sent tnx']=df_KDE['Sent tnx'].round().abs()
df_KDE['Received Tnx']=df_KDE['Received Tnx'].round().abs()
df_KDE['Number of Created Contracts']=df_KDE['Number of Created Contracts'].round().abs()

print(df_KDE.head(10))

import seaborn as sns
import matplotlib.pyplot as plt

columns = df.columns

plt.figure(figsize=(15, 10))

x_limits = {
    'FLAG': (-1, 2),
    'Avg min between sent tnx': (-20000, 50000),
    'Avg min between received tnx': (-20000, 50000),
    'Time Diff between first and last (Mins)': (-200000, 2000000),
    'Sent tnx': (-1000, 1000),
    'Received Tnx': (-1000, 1000),
    'Number of Created Contracts': (-100, 100),
    'max value received': (-2000, 10000),
    'avg val received': (-2000, 5000),
    'avg val sent': (-500, 500),
    'total Ether sent': (-100000, 200000),
    'total ether balance': (-1000000, 1000000),
    'ERC20 total Ether received': (-50000, 50000),
    'ERC20 total ether sent': (-5000, 5000)
}

for i, col in enumerate(columns, 1):
    plt.subplot(3, 5, i)
    sns.kdeplot(df[col], label='Real', color='red')
    sns.kdeplot(df_KDE[col], label='Synthetic', color='blue')
    plt.title(f' {col}')
    plt.legend()


    if col in x_limits:
        plt.xlim(x_limits[col])

plt.tight_layout()
plt.show()

import numpy as np

from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import MinMaxScaler

data = df

scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

gmm = GaussianMixture(n_components=5, covariance_type='full')
gmm.fit(data_scaled)

samples, _ = gmm.sample(19682)
samples_denorm = scaler.inverse_transform(samples)
df_GMM = pd.DataFrame(samples_denorm, columns=data.columns)

print(df_GMM.head())

df_GMM['FLAG']=df_GMM['FLAG'].round().abs()
df_GMM['Sent tnx']=df_GMM['Sent tnx'].round().abs()
df_GMM['Received Tnx']=df_GMM['Received Tnx'].round().abs()
df_GMM['Number of Created Contracts']=df_GMM['Number of Created Contracts'].round().abs()

print(df_GMM.head(10))

import seaborn as sns
import matplotlib.pyplot as plt

columns = df.columns

plt.figure(figsize=(15, 10))

x_limits = {
    'FLAG': (-1, 2),
    'Avg min between sent tnx': (-20000, 50000),
    'Avg min between received tnx': (-20000, 50000),
    'Time Diff between first and last (Mins)': (-200000, 2000000),
    'Sent tnx': (-1000, 1000),
    'Received Tnx': (-1000, 1000),
    'Number of Created Contracts': (-100, 100),
    'max value received': (-2000, 10000),
    'avg val received': (-2000, 5000),
    'avg val sent': (-500, 500),
    'total Ether sent': (-200000, 200000),
    'total ether balance': (-1000000, 1000000),
    'ERC20 total Ether received': (-50000, 50000),
    'ERC20 total ether sent': (-5000, 5000)
}

for i, col in enumerate(columns, 1):
    plt.subplot(3, 5, i)
    sns.kdeplot(df[col], label='Real', color='red')
    sns.kdeplot(df_GMM[col], label='Synthetic', color='blue')
    plt.title(f' {col}')
    plt.legend()


    if col in x_limits:
        plt.xlim(x_limits[col])

plt.tight_layout()
plt.show()

from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def train_and_evaluate_model(X_train, y_train, X_test, y_test):
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro')
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    return accuracy, precision, recall, f1

def print_results(name, results):
    print(f"{name} Results:")
    print(f"Accuracy: {results[0]:.4f}")
    print(f"Precision: {results[1]:.4f}")
    print(f"Recall: {results[2]:.4f}")
    print(f"F1 Score: {results[3]:.4f}")
    print("\n")

df_CTGAN['FLAG'] = df_CTGAN['FLAG'].astype(int)
df_DCGAN['FLAG'] = df_DCGAN['FLAG'].astype(int)
df_VAE['FLAG'] = df_VAE['FLAG'].astype(int)
df_KDE['FLAG'] = df_KDE['FLAG'].astype(int)
df_GMM['FLAG'] = df_GMM['FLAG'].astype(int)
df_GAN['FLAG'] = df_GAN['FLAG'].astype(int)
df_TVAE['FLAG'] = df_TVAE['FLAG'].astype(int)


X_train, X_test, y_train, y_test = train_test_split(df.drop(columns=['FLAG']), df['FLAG'], test_size=0.2, random_state=42)
X_train_ctgan, X_test_ctgan, y_train_ctgan, y_test_ctgan = train_test_split(df_CTGAN.drop(columns=['FLAG']), df_CTGAN['FLAG'], test_size=0.2, random_state=42)
X_train_dcgan, X_test_dcgan, y_train_dcgan, y_test_dcgan = train_test_split(df_DCGAN.drop(columns=['FLAG']), df_DCGAN['FLAG'], test_size=0.2, random_state=42)
X_train_vae, X_test_vae, y_train_vae, y_test_vae = train_test_split(df_VAE.drop(columns=['FLAG']), df_VAE['FLAG'], test_size=0.2, random_state=42)
X_train_kde, X_test_kde, y_train_kde, y_test_kde = train_test_split(df_KDE.drop(columns=['FLAG']), df_KDE['FLAG'], test_size=0.2, random_state=42)
X_train_gmm, X_test_gmm, y_train_gmm, y_test_gmm = train_test_split(df_GMM.drop(columns=['FLAG']), df_GMM['FLAG'], test_size=0.2, random_state=42)
X_train_gan, X_test_gan, y_train_gan, y_test_gan = train_test_split(df_GAN.drop(columns=['FLAG']), df_GAN['FLAG'], test_size=0.2, random_state=42)
X_train_tvae, X_test_tvae, y_train_tvae, y_test_tvae = train_test_split(df_TVAE.drop(columns=['FLAG']), df_TVAE['FLAG'], test_size=0.2, random_state=42)


results_original = train_and_evaluate_model(X_train, y_train, X_test, y_test)
print_results("Original Data", results_original)

results_ctgan = train_and_evaluate_model(X_train_ctgan, y_train_ctgan, X_test_ctgan, y_test_ctgan)
print_results("CTGAN Synthetic Data", results_ctgan)

results_dcgan = train_and_evaluate_model(X_train_dcgan, y_train_dcgan, X_test_dcgan, y_test_dcgan)
print_results("DCGAN Synthetic Data", results_dcgan)

results_vae = train_and_evaluate_model(X_train_vae, y_train_vae, X_test_vae, y_test_vae)
print_results("VAE Synthetic Data", results_vae)

results_kde = train_and_evaluate_model(X_train_kde, y_train_kde, X_test_kde, y_test_kde)
print_results("KDE Synthetic Data", results_kde)

results_gmm = train_and_evaluate_model(X_train_gmm, y_train_gmm, X_test_gmm, y_test_gmm)
print_results("GMM Synthetic Data", results_gmm)

results_gan = train_and_evaluate_model(X_train_gan, y_train_gan, X_test_gan, y_test_gan)
print_results("GAN Synthetic Data", results_gan)

results_tvae = train_and_evaluate_model(X_train_tvae, y_train_tvae, X_test_tvae, y_test_tvae)
print_results("TVAE Synthetic Data", results_tvae)

from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

preprocessor = SimpleImputer(strategy="most_frequent")

def train_and_evaluate_model(X_train, y_train, X_test, y_test, model):
    clf = Pipeline(steps=[('preprocessor', preprocessor),
                          ('classifier', model)])

    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro')
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')

    return accuracy, precision, recall, f1

def print_results(name, results):
    print(f"{name} Results:")
    print(f"Accuracy: {results[0]:.4f}")
    print(f"Precision: {results[1]:.4f}")
    print(f"Recall: {results[2]:.4f}")
    print(f"F1 Score: {results[3]:.4f}")
    print("\n")

X_train, X_test, y_train, y_test = train_test_split(df.drop(columns=['FLAG']), df['FLAG'], test_size=0.2, random_state=42)

results_nb = train_and_evaluate_model(X_train, y_train, X_test, y_test, GaussianNB())
print_results("Naive Bayes", results_nb)

X_train_ctgan, X_test_ctgan, y_train_ctgan, y_test_ctgan = train_test_split(df_CTGAN.drop(columns=['FLAG']), df_CTGAN['FLAG'], test_size=0.2, random_state=42)
results_ctgan = train_and_evaluate_model(X_train_ctgan, y_train_ctgan, X_test_ctgan, y_test_ctgan, GaussianNB())
print_results("CTGAN Synthetic Data", results_ctgan)

X_train_dcgan, X_test_dcgan, y_train_dcgan, y_test_dcgan = train_test_split(df_DCGAN.drop(columns=['FLAG']), df_DCGAN['FLAG'], test_size=0.2, random_state=42)
results_dcgan = train_and_evaluate_model(X_train_dcgan, y_train_dcgan, X_test_dcgan, y_test_dcgan, GaussianNB())
print_results("DCGAN Synthetic Data", results_dcgan)

X_train_vae, X_test_vae, y_train_vae, y_test_vae = train_test_split(df_VAE.drop(columns=['FLAG']), df_VAE['FLAG'], test_size=0.2, random_state=42)
results_vae = train_and_evaluate_model(X_train_vae, y_train_vae, X_test_vae, y_test_vae, GaussianNB())
print_results("VAE Synthetic Data", results_vae)

X_train_kde, X_test_kde, y_train_kde, y_test_kde = train_test_split(df_KDE.drop(columns=['FLAG']), df_KDE['FLAG'], test_size=0.2, random_state=42)
results_kde = train_and_evaluate_model(X_train_kde, y_train_kde, X_test_kde, y_test_kde, GaussianNB())
print_results("KDE Synthetic Data", results_kde)

X_train_gmm, X_test_gmm, y_train_gmm, y_test_gmm = train_test_split(df_GMM.drop(columns=['FLAG']), df_GMM['FLAG'], test_size=0.2, random_state=42)
results_gmm = train_and_evaluate_model(X_train_gmm, y_train_gmm, X_test_gmm, y_test_gmm, GaussianNB())
print_results("GMM Synthetic Data", results_gmm)

X_train_gan, X_test_gan, y_train_gan, y_test_gan = train_test_split(df_GAN.drop(columns=['FLAG']), df_GAN['FLAG'], test_size=0.2, random_state=42)
results_gan = train_and_evaluate_model(X_train_gan, y_train_gan, X_test_gan, y_test_gan, GaussianNB())
print_results("GAN Synthetic Data", results_gan)

X_train_tvae, X_test_tvae, y_train_tvae, y_test_tvae = train_test_split(df_TVAE.drop(columns=['FLAG']), df_TVAE['FLAG'], test_size=0.2, random_state=42)
results_tvae = train_and_evaluate_model(X_train_tvae, y_train_tvae, X_test_tvae, y_test_tvae, GaussianNB())
print_results("TVAE Synthetic Data", results_tvae)

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

preprocessor = SimpleImputer(strategy="most_frequent")

def train_and_evaluate_model(X_train, y_train, X_test, y_test, model):
    clf = Pipeline(steps=[('preprocessor', preprocessor),
                          ('classifier', model)])
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro')
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    return accuracy, precision, recall, f1

def print_results(name, results):
    print(f"{name} Results:")
    print(f"Accuracy: {results[0]:.4f}")
    print(f"Precision: {results[1]:.4f}")
    print(f"Recall: {results[2]:.4f}")
    print(f"F1 Score: {results[3]:.4f}")
    print("\n")

X_train, X_test, y_train, y_test = train_test_split(df.drop(columns=['FLAG']), df['FLAG'], test_size=0.2, random_state=42)

results_knn = train_and_evaluate_model(X_train, y_train, X_test, y_test, KNeighborsClassifier())
print_results("KNN", results_knn)

X_train_ctgan, X_test_ctgan, y_train_ctgan, y_test_ctgan = train_test_split(df_CTGAN.drop(columns=['FLAG']), df_CTGAN['FLAG'], test_size=0.2, random_state=42)
results_ctgan = train_and_evaluate_model(X_train_ctgan, y_train_ctgan, X_test_ctgan, y_test_ctgan, KNeighborsClassifier())
print_results("CTGAN Synthetic Data", results_ctgan)

X_train_dcgan, X_test_dcgan, y_train_dcgan, y_test_dcgan = train_test_split(df_DCGAN.drop(columns=['FLAG']), df_DCGAN['FLAG'], test_size=0.2, random_state=42)
results_dcgan = train_and_evaluate_model(X_train_dcgan, y_train_dcgan, X_test_dcgan, y_test_dcgan, KNeighborsClassifier())
print_results("DCGAN Synthetic Data", results_dcgan)

X_train_vae, X_test_vae, y_train_vae, y_test_vae = train_test_split(df_VAE.drop(columns=['FLAG']), df_VAE['FLAG'], test_size=0.2, random_state=42)
results_vae = train_and_evaluate_model(X_train_vae, y_train_vae, X_test_vae, y_test_vae, KNeighborsClassifier())
print_results("VAE Synthetic Data", results_vae)

X_train_kde, X_test_kde, y_train_kde, y_test_kde = train_test_split(df_KDE.drop(columns=['FLAG']), df_KDE['FLAG'], test_size=0.2, random_state=42)
results_kde = train_and_evaluate_model(X_train_kde, y_train_kde, X_test_kde, y_test_kde, KNeighborsClassifier())
print_results("KDE Synthetic Data", results_kde)

X_train_gmm, X_test_gmm, y_train_gmm, y_test_gmm = train_test_split(df_GMM.drop(columns=['FLAG']), df_GMM['FLAG'], test_size=0.2, random_state=42)
results_gmm = train_and_evaluate_model(X_train_gmm, y_train_gmm, X_test_gmm, y_test_gmm, KNeighborsClassifier())
print_results("GMM Synthetic Data", results_gmm)

X_train_gan, X_test_gan, y_train_gan, y_test_gan = train_test_split(df_GAN.drop(columns=['FLAG']), df_GAN['FLAG'], test_size=0.2, random_state=42)
results_gan = train_and_evaluate_model(X_train_gan, y_train_gan, X_test_gan, y_test_gan, KNeighborsClassifier())
print_results("GAN Synthetic Data", results_gan)

X_train_tvae, X_test_tvae, y_train_tvae, y_test_tvae = train_test_split(df_TVAE.drop(columns=['FLAG']), df_TVAE['FLAG'], test_size=0.2, random_state=42)
results_tvae = train_and_evaluate_model(X_train_tvae, y_train_tvae, X_test_tvae, y_test_tvae, KNeighborsClassifier())
print_results("TVAE Synthetic Data", results_tvae)

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import pandas as pd

preprocessor = SimpleImputer(strategy="most_frequent")

def train_and_evaluate_model(X_train, y_train, X_test, y_test, model):
    clf = Pipeline(steps=[('preprocessor', preprocessor),
                          ('classifier', model)])
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro')
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    return accuracy, precision, recall, f1

def print_results(name, results):
    print(f"{name} Results:")
    print(f"Accuracy: {results[0]:.4f}")
    print(f"Precision: {results[1]:.4f}")
    print(f"Recall: {results[2]:.4f}")
    print(f"F1 Score: {results[3]:.4f}")
    print("\n")

X_train, X_test, y_train, y_test = train_test_split(df.drop(columns=['FLAG']), df['FLAG'], test_size=0.2, random_state=42)

results_tree = train_and_evaluate_model(X_train, y_train, X_test, y_test, DecisionTreeClassifier())
print_results("Decision Tree", results_tree)

X_train_ctgan, X_test_ctgan, y_train_ctgan, y_test_ctgan = train_test_split(df_CTGAN.drop(columns=['FLAG']), df_CTGAN['FLAG'], test_size=0.2, random_state=42)
results_ctgan = train_and_evaluate_model(X_train_ctgan, y_train_ctgan, X_test_ctgan, y_test_ctgan, DecisionTreeClassifier())
print_results("CTGAN Synthetic Data", results_ctgan)

X_train_dcgan, X_test_dcgan, y_train_dcgan, y_test_dcgan = train_test_split(df_DCGAN.drop(columns=['FLAG']), df_DCGAN['FLAG'], test_size=0.2, random_state=42)
results_dcgan = train_and_evaluate_model(X_train_dcgan, y_train_dcgan, X_test_dcgan, y_test_dcgan, DecisionTreeClassifier())
print_results("DCGAN Synthetic Data", results_dcgan)

X_train_vae, X_test_vae, y_train_vae, y_test_vae = train_test_split(df_VAE.drop(columns=['FLAG']), df_VAE['FLAG'], test_size=0.2, random_state=42)
results_vae = train_and_evaluate_model(X_train_vae, y_train_vae, X_test_vae, y_test_vae, DecisionTreeClassifier())
print_results("VAE Synthetic Data", results_vae)

X_train_kde, X_test_kde, y_train_kde, y_test_kde = train_test_split(df_KDE.drop(columns=['FLAG']), df_KDE['FLAG'], test_size=0.2, random_state=42)
results_kde = train_and_evaluate_model(X_train_kde, y_train_kde, X_test_kde, y_test_kde, DecisionTreeClassifier())
print_results("KDE Synthetic Data", results_kde)

X_train_gmm, X_test_gmm, y_train_gmm, y_test_gmm = train_test_split(df_GMM.drop(columns=['FLAG']), df_GMM['FLAG'], test_size=0.2, random_state=42)
results_gmm = train_and_evaluate_model(X_train_gmm, y_train_gmm, X_test_gmm, y_test_gmm, DecisionTreeClassifier())
print_results("GMM Synthetic Data", results_gmm)

X_train_gan, X_test_gan, y_train_gan, y_test_gan = train_test_split(df_GAN.drop(columns=['FLAG']), df_GAN['FLAG'], test_size=0.2, random_state=42)
results_gan = train_and_evaluate_model(X_train_gan, y_train_gan, X_test_gan, y_test_gan, DecisionTreeClassifier())
print_results("GAN Synthetic Data", results_gan)

X_train_tvae, X_test_tvae, y_train_tvae, y_test_tvae = train_test_split(df_TVAE.drop(columns=['FLAG']), df_TVAE['FLAG'], test_size=0.2, random_state=42)
results_tvae = train_and_evaluate_model(X_train_tvae, y_train_tvae, X_test_tvae, y_test_tvae, DecisionTreeClassifier())
print_results("TVAE Synthetic Data", results_tvae)