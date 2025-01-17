import datetime
import os
import sys

import numpy as np
import pandas as pd

from imblearn.over_sampling import SMOTE, BorderlineSMOTE, SVMSMOTE, ADASYN
# from sklearn.model_selection import train_test_split


def load_transformer_embeddings_data(dataset_file):
    print(f'Reading file: {dataset_file.split("/")[-1]}')
    df = pd.read_csv(dataset_file, sep='\t', on_bad_lines='skip')

    print('Generating embeddings list...')
    mwe_embedding = np.array([
        np.array([float(elem) for elem in line.split(',')])
        for line in df['mwe_embedding'].tolist()
    ])
    first_word_only_embedding = np.array([
        np.array([float(elem) for elem in line.split(',')])
        for line in df['first_word_only_embedding'].tolist()
    ])
    second_word_only_embedding = np.array([
        np.array([float(elem) for elem in line.split(',')])
        for line in df['second_word_only_embedding'].tolist()
    ])
    first_word_mwe_emb_diff = np.array([
        np.array([float(elem) for elem in line.split(',')])
        for line in df['first_word_mwe_emb_diff'].tolist()
    ])
    second_word_mwe_emb_diff = np.array([
        np.array([float(elem) for elem in line.split(',')])
        for line in df['second_word_mwe_emb_diff'].tolist()
    ])
    first_word_mwe_emb_abs_diff = np.array([
        np.array([float(elem) for elem in line.split(',')])
        for line in df['first_word_mwe_emb_abs_diff'].tolist()
    ])
    second_word_mwe_emb_abs_diff = np.array([
        np.array([float(elem) for elem in line.split(',')])
        for line in df['second_word_mwe_emb_abs_diff'].tolist()
    ])
    first_word_mwe_emb_prod = np.array([
        np.array([float(elem) for elem in line.split(',')])
        for line in df['first_word_mwe_emb_prod'].tolist()
    ])
    second_word_mwe_emb_prod = np.array([
        np.array([float(elem) for elem in line.split(',')])
        for line in df['second_word_mwe_emb_prod'].tolist()
    ])

    embeddings_list = np.hstack(
        (mwe_embedding, first_word_only_embedding, second_word_only_embedding,
         first_word_mwe_emb_diff, second_word_mwe_emb_diff,
         first_word_mwe_emb_abs_diff, second_word_mwe_emb_abs_diff,
         first_word_mwe_emb_prod, second_word_mwe_emb_prod))

    embeddings_list = np.array([
        ','.join([str(elem) for elem in embedding])
        for embedding in embeddings_list
    ])

    df['combined_embedding'] = embeddings_list

    return df


def get_curr_time():
    return f'{datetime.datetime.now().strftime("%H:%M:%S")}'


def save_mwe_list(embeddings_list, labels_list, filepath):
    with open(filepath, 'w') as out_file:
        out_file.write('\t'.join(['combined_embedding', 'is_correct']) + '\n')

        for emb_ind, emb in enumerate(embeddings_list):
            out_file.write('\t'.join([
                ','.join([str(elem) for elem in emb]),
                str(labels_list[emb_ind])
            ]) + '\n')


def get_smote_oversampler(smote_key):
    smote_dict = {
        'smote': SMOTE(),
        'borderline': BorderlineSMOTE(),
        'svm': SVMSMOTE(),
        'adasyn': ADASYN()
    }

    return smote_dict[smote_key]


def generate_smote_datasets(filepath, num_samples):
    result_dir_name = os.path.join(os.path.join(*filepath.split('/')[:-1]))

    file_name = filepath.split('/')[-1].split('.')[0]
    print(f'{get_curr_time()} : Loading data...')
    df = pd.read_csv(filepath, sep='\t', on_bad_lines='skip')

    # SMOTE, Borderline SMOTE, SVM-SMOTE and ADASYN dataset variants
    for smote_type in ['smote', 'borderline', 'svm', 'adasyn'][2:-1]:
        print(
            f'{get_curr_time()} : Generating {smote_type} dataset variant...')

        oversample = get_smote_oversampler(smote_type)
        print(f'{get_curr_time()} : Getting train samples...')
        X_train = df[(df['dataset_type'] == 'train') |
                     (df['dataset_type'] == 'null'
                      )]['combined_embedding'].tolist()[:num_samples]
        print(f'{get_curr_time()} : Ommiting difference vectors...')
        X_train = np.array([
            np.array([
                float(elem) for elem in (embedding.split(',')[:768 * 2] +
                                         embedding.split(',')[768 * 3:])
            ]) for embedding in X_train
        ])
        print(f'{get_curr_time()} : Getting labels...')
        y_train = df[(df['dataset_type'] == 'train') | (
            df['dataset_type'] == 'null')]['is_correct'].tolist()[:num_samples]
        print(f'{get_curr_time()} : Generating synthetic samples...')
        transformed_X_train, transformed_y_train = oversample.fit_resample(
            X_train, y_train)

        print(
            f'{get_curr_time()} : Saving dataframe to: {os.path.join(result_dir_name, f"{file_name}_{smote_type}.tsv")}'
        )

        save_mwe_list(
            transformed_X_train, transformed_y_train,
            os.path.join(result_dir_name, f'{file_name}_{smote_type}.tsv'))


def main(args):
    num_samples = 200000
    for filepath in args:
        generate_smote_datasets(filepath, num_samples)


if __name__ == '__main__':
    main(sys.argv[1:])
