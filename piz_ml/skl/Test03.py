"""多分类，SVM处理多分类"""
import numpy as np
import jieba
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC, LinearSVC

from piz_base import PathUtils, IOUtils
from piz_ml.skl import helper


def read_dataset(name, stopwords):
    path = PathUtils.to_file_path(__file__, "data", name + "_data.txt")

    with IOUtils.get_resource_as_stream(path, encoding="UTF-8") as f:
        feature_list = [helper.filter_stopword(stopwords, jieba.cut(i.strip())) for i in f.readlines()]
    path = PathUtils.to_file_path(__file__, "data", name + "_label.txt")

    with IOUtils.get_resource_as_stream(path, encoding="UTF-8") as f:
        label_list = [i.strip() for i in f.readlines()]

    return feature_list, label_list


def train(name):
    stopwords = helper.read_stopwords()
    (feature_list, label_list) = read_dataset(name, stopwords)
    le = LabelEncoder()
    train_label = le.fit_transform(label_list)
    helper.dump(le, name + "_label.sav")
    classifier = Pipeline([
        ('vectorizer', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', OneVsRestClassifier(LinearSVC()))])
    classifier.fit(feature_list, train_label)
    helper.dump(classifier, name + "_model.sav")
    score = classifier.score(feature_list, train_label)
    print(score)


def to_sample(target, stopwords):
    return helper.filter_stopword(stopwords, jieba.cut(target.strip()))


def predict(name, target):
    stopwords = helper.read_stopwords()
    features = to_sample(target, stopwords)
    classifier = helper.load(name + "_model.sav")
    result = classifier.predict([features])
    le: LabelEncoder = helper.load(name + "_label.sav")
    result = le.inverse_transform(result)
    print(result)


if __name__ == "__main__":
    # train("sample03")
    sample = '使用过程中，使用数据采集器故障红灯亮，并有XYZ告警信息，使用数据采集器故障,' \
             'SGJL设备软件及FHJL器软件存在问题，导致故障灯亮起闪烁问题为：DSP取数据FIF0溢出；' \
             '以太网接收错误，FHJL器记录数据分段,"1234厂需对SGJL设备软件进行升级，000厂需对FHJL器软件进行升级。' \
             '研究院对升级软件验证入库后发使用技术单对公司设备进行升级"'
    predict("sample03", sample)
    GridSearchCV
