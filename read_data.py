from sklearn import datasets 
import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import os


def split_data(X, y, N_agent, even=True):
    '''
    split the data to N_agent chunks. Will remove the remainder data if all data didn't split evenly
    '''
    if even:
        N_data_dist_prob = np.ones(N_agent) / N_agent
    else:
        N_data_dist_prob = np.random.rand(N_agent) + 0.2
        N_data_dist_prob = N_data_dist_prob / sum(N_data_dist_prob)


    N = X.shape[0]

    N_data_agent_list = N_data_dist_prob * N
    N_data_agent_list = N_data_agent_list.astype(int)
    N_data = np.sum(N_data_agent_list)

    X, y = X[0:N_data], y[0:N_data].reshape(-1, 1)

    N_data_boundary = np.hstack( (0, np.cumsum(N_data_agent_list)) )

    N_data_agent_mean = N_data // N_agent

    return X, y, N_data_boundary, N_data_agent_mean

def read_cov():
    covtype=datasets.fetch_covtype(data_home='./real_data')
    # extract only two label data 
    mask = np.in1d(covtype.target, [1,2])
    covtype.data = covtype.data[mask]
    covtype.target = covtype.target[mask]
    # preprocessing
    std = sklearn.preprocessing.StandardScaler()
    norm = sklearn.preprocessing.Normalizer()
    covtype.data = norm.fit_transform(covtype.data)
    X_train, X_test, y_train, y_test = train_test_split(covtype.data, covtype.target, test_size=0.6)
    y_train[y_train==2] = -1
    y_test[y_test==2] = -1

    return X_train, y_train[:, np.newaxis]

def read_mnist():
    import tensorflow.examples.tutorials.mnist.input_data as input_data
    file_loc=os.path.abspath('C:/Users/biche/OneDrive/Documents/Python Scripts/random_reshuffle/MNIST_data') 
    ds = input_data.read_data_sets(file_loc, one_hot=False)
    X = ds.train.images
    y = ds.train.labels

    mask = np.in1d(y, [0,1])
    normalizer = sklearn.preprocessing.Normalizer()
    X= X[mask]
    X_train = normalizer.fit_transform(X)
    y = y[mask]
    y_train = (y-0.5)*2
    print (y_train)

    return X_train, y_train[:, np.newaxis]

def read_cifar():
    def unpickle(file):
        import pickle
        with open(file, 'rb') as fo:
            dict = pickle.load(fo, encoding='bytes')
        return dict

    file_loc=os.path.abspath('C:/Users/biche/OneDrive/Documents/Python Scripts/random_reshuffle/real_data/cifar-10') 
    cifar_data = unpickle(os.path.join(file_loc,'data_batch_1'))
    cifar_data_test = unpickle(os.path.join(file_loc,'test_batch'))

    X_cifar_train = cifar_data[b'data']
    y_cifar_train = np.array(cifar_data[b'labels'])
    X_cifar_test = cifar_data_test[b'data']
    y_cifar_test = np.array(cifar_data_test[b'labels'])

    mask_train = np.in1d(y_cifar_train, [0,1])
    mask_test = np.in1d(y_cifar_test, [0,1])

    X_cifar_train = X_cifar_train[mask_train]
    y_cifar_train = y_cifar_train[mask_train]
    X_cifar_test = X_cifar_test[mask_test]
    y_cifar_test = y_cifar_test[mask_test]

    normalizer = sklearn.preprocessing.Normalizer()
    std = sklearn.preprocessing.StandardScaler()
    X_cifar_train = normalizer.fit_transform(X_cifar_train)
    X_cifar_test = normalizer.transform(X_cifar_test)
    y_cifar_train[y_cifar_train==0] = -1
    y_cifar_test[y_cifar_test==0] = -1

    return X_cifar_train, y_cifar_train[:, np.newaxis]