"""多分类，并行处理，流水线学习，Tfidf文本特征提取"""
import csv
import jieba
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from piz_base import IOUtils, PathUtils
from piz_ml.skl import helper


def cut_word(target, stopwords):
    seg_list = jieba.cut(target)
    return helper.filter_stopword(stopwords, seg_list) if stopwords else " ".join(seg_list)


def read_dataset(name, stopwords=None):
    feature_list = []
    label_list = []
    path = PathUtils.to_file_path(__file__, "data", name + ".csv")

    with IOUtils.get_resource_as_stream(path, encoding="gbk") as f:
        reader = csv.reader(f)
        headers = next(reader)

        for row in reader:
            label_list.append(row[-1])
            row_dic = {}

            for i, item in enumerate(row[:-1]):
                row_dic[headers[i]] = cut_word(item, stopwords)
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


def train(name):
    stopwords = helper.read_stopwords()
    (feature_list, label_list, headers) = read_dataset(name, stopwords)
    feature_dict = transform(feature_list, headers)
    le = LabelEncoder()
    dummy_y = le.fit_transform(label_list)
    helper.dump(le, name + "_label.sav")
    # 流水线学习器
    classifier = Pipeline([
        # 并行处理
        ('union', FeatureUnion(
            transformer_list=[
                ('故障现象', Pipeline([
                    ('selector', ItemSelector(key='故障现象')),
                    # 词频特征提取
                    ('tfidf', TfidfVectorizer(analyzer='char_wb', token_pattern=r"(?u)\b\w+\b", min_df=1)),
                ])),
                ('原因分析', Pipeline([
                    ('selector', ItemSelector(key='原因分析')),
                    ('tfidf', TfidfVectorizer(analyzer='char_wb', token_pattern=r"(?u)\b\w+\b", min_df=1)),
                ])),
                ('处理意见及结果', Pipeline([
                    ('selector', ItemSelector(key='处理意见及结果')),
                    ('tfidf', TfidfVectorizer(analyzer='char_wb', token_pattern=r"(?u)\b\w+\b", min_df=1)),
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
    helper.dump(classifier, name + "_model.sav")
    score = classifier.score(feature_dict, dummy_y)
    print(score)  # 1.0 PS: 样本太少
    # predicted = classifier.predict(feature_dict)
    # rate = (predicted == dummy_y).sum() * 100.0 / len(predicted) * 1.0
    # print("rate %.2f %% " % rate)


def to_sample(target, stopwords):
    seg_list = target.split(",")
    features = np.recarray(
        shape=1,
        dtype=[('故障现象', object), ('原因分析', object), ('处理意见及结果', object)])
    features['故障现象'][0] = cut_word(seg_list[0], stopwords)
    features['原因分析'][0] = cut_word(seg_list[1], stopwords)
    features['处理意见及结果'][0] = cut_word(seg_list[2], stopwords)
    return features


def predict(name, target):
    stopwords = helper.read_stopwords()
    features = to_sample(target, stopwords)
    classifier = helper.load(name + "_model.sav")
    result = classifier.predict(features)
    le: LabelEncoder = helper.load(name + "_label.sav")
    result = le.inverse_transform(result)
    print(result)


if __name__ == '__main__':
    # train("sample02")
    sample = '使用过程中，使用数据采集器故障红灯亮，并有XYZ告警信息，使用数据采集器故障,' \
             'SGJL设备软件及FHJL器软件存在问题，导致故障灯亮起闪烁问题为：DSP取数据FIF0溢出；' \
             '以太网接收错误，FHJL器记录数据分段,"1234厂需对SGJL设备软件进行升级，000厂需对FHJL器软件进行升级。' \
             '研究院对升级软件验证入库后发使用技术单对公司设备进行升级"'
    predict("sample02", sample)






