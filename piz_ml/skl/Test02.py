""""""
import csv
import jieba
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

from piz_base import IOUtils, PathUtils
from piz_ml.skl import helper


def filter_stopword(stopwords, seg_list):
    stopword = stopwords
    del_stopwords_single_txt = []

    for word in seg_list:
        word = word.strip()

        if not word and word not in stopword:
            del_stopwords_single_txt.append(word)
    return " ".join(del_stopwords_single_txt)


def read_stopwords():
    stopwords = set()
    path = PathUtils.to_file_path(__file__, "data", "Dict_Stopwords.txt")

    with IOUtils.get_resource_as_stream(path) as f:
        for line in f.readlines():
            stopwords.add(line.strip())
    return stopwords


def read_dataset(name, stopwords=None):
    feature_list = []
    label_list = []
    path = PathUtils.to_file_path(__file__, "data", name + ".csv")

    with IOUtils.get_resource_as_stream(path) as f:
        reader = csv.reader(f)
        headers = next(reader)

        for row in reader:
            label_list.append(row[-1])
            row_dic = {}

            for i, item in enumerate(row[:-1]):
                seg_list = jieba.cut(item)
                seg_list = filter_stopword(stopwords, seg_list) if stopwords else " ".join(seg_list)
                row_dic[headers[i]] = seg_list
            feature_list.append(row_dic)
    return feature_list, label_list, headers


def transform(feature_list, heads):
    features = np.recarray(
        shape=len(feature_list),
        dtype=[('故障现象', object), ('原因分析', object), ('处理意见及结果', object)])

    for i, item in enumerate(feature_list):
        features['故障现象'][i] = item[heads[0]]
        features['原因分析'][i] = item[heads[1]]
        features['处理意见及结果'][i] = item[heads[2]]
    return features


class ItemSelector(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[self.key]


def main():
    stopwords = read_stopwords()
    (feature_list, label_list, headers) = read_dataset("sample02", stopwords)
    feature_dict = transform(feature_list, headers)
    lb = LabelEncoder()
    dummy_y = lb.fit_transform(label_list)
    helper.dump(lb, "sample02" + "_label.sav")
    # 流水线学习器
    classifier = Pipeline([
        # 并行处理
        ('union', FeatureUnion(
            transformer_list=[
                ('故障现象', Pipeline([
                    ('selector', ItemSelector(key='故障现象')),
                    # 词频特征提取
                    ('tfidf', TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", min_df=1)),
                ])),
                ('原因分析', Pipeline([
                    ('selector', ItemSelector(key='原因分析')),
                    ('tfidf', TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", min_df=1)),
                ])),
                ('处理意见及结果', Pipeline([
                    ('selector', ItemSelector(key='处理意见及结果')),
                    ('tfidf', TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", min_df=1)),
                ])),
            ],
            transformer_weights={
                '故障现象': 2.0,
                '原因分析': 1.5,
                '处理意见及结果': 1.0,
            },
        )),
        # ('svc', SVC(kernel='linear')),
        ('RFC', RandomForestClassifier())
    ])
    classifier.fit(feature_dict, dummy_y)
    helper.dump(classifier, "sample02" + "_model.sav")


if __name__ == '__main__':
    main()






