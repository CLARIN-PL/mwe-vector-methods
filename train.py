import re
import sys

import numpy as np
import pandas as pd

from cnn import get_cnn_model_pred
from logistic_regression import get_lr_model_pred
from random_forest import get_rf_model_pred

from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from tensorflow import one_hot


def load_data(dataset_file):
    dataset = np.load(dataset_file)

    X = np.array([elem[:900] for elem in dataset])

    y = np.array([elem[900] for elem in dataset])
    y = y.astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        test_size=0.20,
                                                        random_state=42)

    return X_train, X_test, y_train, y_test


def load_transformer_embeddings_data(dataset_file):
    print(f'Reading file: {dataset_file.split("/")[-1]}')
    df = pd.read_csv(dataset_file, sep='\t', header=None)

    print('Generating embeddings list...')
    df[4] = df[0] + ',' + df[1] + ',' + df[2]

    embeddings_list = [elem.split(',') for elem in df[4].tolist()]
    print(f'embeddings_list[0] len: {len(embeddings_list[0])}')
    for sentence in embeddings_list:
        for val in sentence:
            print(f'val: {val}')
            print(float(re.findall(r"[-+]?\d*\.\d+|\d+", val)[0]))
    embeddings_list = [[float(re.findall(r"[-+]?\d*\.\d+|\d+", val)[0]) for val in sentence] for sentence in embeddings_list[:-1]]

    X = np.array(embeddings_list)

    y = df[3].tolist()
    y = y.astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        test_size=0.20,
                                                        random_state=42)

    return X_train, X_test, y_train, y_test


def get_evaluation_report(y_true, y_pred):
    target_names = ['Incorrect MWE', 'Correct MWE']

    print(classification_report(y_true, y_pred, target_names=target_names))


def main(args):
    if 'transformer_embeddings' in args:
        dataset_filepath = 'sentences_containing_mwe_from_kgr10_group_0_embeddings_1_layers_incomplete_mwe_in_sent.tsv'

        X_train, X_test, y_train, y_test = load_transformer_embeddings_data(dataset_filepath)

    else:
        dataset_filepath = 'mwe_dataset.npy'
        # dataset_filepath = 'mwe_dataset_cbow.npy'
        # dataset_filepath = 'mwe_dataset_domain_balanced.npy'  # domain-balanced dataset

        X_train, X_test, y_train, y_test = load_data(dataset_filepath)

    if 'cnn' in args:
        X_train = np.reshape(X_train, [X_train.shape[0], X_train.shape[1], 1])
        X_test = np.reshape(X_test, [X_test.shape[0], X_train.shape[1], 1])
        y_train = one_hot(y_train, depth=2)

        if 'eval' in args:
            eval_only = True
            model_path = args[2]
        else:
            eval_only = False
            model_path = None

        y_pred = get_cnn_model_pred(X_train, y_train, X_test,
                                    eval_only=eval_only,
                                    model_path=model_path,
                                    input_shape=(X_train.shape[1], 1))

        y_pred = [np.argmax(probs) for probs in y_pred]

    elif 'lr' in args:
        y_pred = get_lr_model_pred(X_train, y_train, X_test)

    elif 'rf' in args:
        y_pred = get_rf_model_pred(X_train, y_train, X_test)

    get_evaluation_report(y_test, y_pred)


if __name__ == '__main__':
    main(sys.argv[1:])
