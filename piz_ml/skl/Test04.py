"""训练，预测，合并权重，流水线学习"""
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.svm import LinearSVC, SVC, SVR, LinearSVR
from sklearn.tree import DecisionTreeClassifier
from xgboost.sklearn import XGBClassifier

from piz_base import PathUtils, IOUtils, DateUtils
from piz_ml.skl import helper

NAMES = [t for t in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]


def read_dataset(name):
    feature_list = []
    label_list = []
    path = PathUtils.to_file_path(__file__, "data", name + ".txt")

    with IOUtils.get_resource_as_stream(path, encoding="UTF-8") as f:
        for line in f.readlines():
            if line.startswith("__label__") and len(line) > 11:
                c = line[11:]
                n = line[11:12].upper()
                age = NAMES.index(n) + 20 if n in NAMES else 30
                feature_list.append([c, {"author": n + "_USER" if n in NAMES else "UNKNOWN", "age": age}])
                label_list.append(int(line[9:10]))

    return feature_list, label_list


class ItemSelector(BaseEstimator, TransformerMixin):
    def __init__(self, index):
        self.index = index

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[:, self.index]


def create_feature(name):
    time1 = DateUtils.current_time_millis()
    feature_list, label_list = read_dataset(name)
    time2 = DateUtils.current_time_millis()
    print("LOAD COMPLETE:{}ms".format(time2 - time1))
    feature_list = np.array(feature_list)
    stop_words = helper.read_stopwords()
    union = FeatureUnion(
        transformer_list=[
            ("feature", Pipeline([
                ('selector', ItemSelector(1)),
                ("dvec", DictVectorizer(
                    sparse=False))
            ])),
            ("content", Pipeline([
                ('selector', ItemSelector(0)),
                ('cvec', CountVectorizer(
                    # analyzer='char_wb',
                    token_pattern=r"(?u)\b\w+\b",
                    min_df=1,
                    stop_words=stop_words)),
                ('tfidf', TfidfTransformer())
            ]))
        ],
        transformer_weights={"feature": 1.0, "content": 1.0})
    feature_list = union.fit_transform(feature_list)
    time1 = DateUtils.current_time_millis()
    print("TRANSFORM COMPLETE:{}ms".format(time1 - time2))
    # dvec: CountVectorizer = union.transformer_list[0][1].named_steps["dvec"]
    # helper.dump(dvec, name + "_dvec.sav")
    # cvec: CountVectorizer = union.transformer_list[1][1].named_steps["cvec"]
    # helper.dump(cvec, name + "_cvec.sav")
    helper.dump(union, name + "_vec.sav")
    time2 = DateUtils.current_time_millis()
    print("DUMP VECTOR COMPLETE:{}ms".format(time2 - time1))
    helper.dump(feature_list, name + "_data.sav")
    helper.dump(label_list, name + "_label.sav")
    time1 = DateUtils.current_time_millis()
    print("DUMP FEATURE COMPLETE:{}ms".format(time1 - time2))


def load_data(name, size):
    feature_list = helper.load(name + "_data.sav")
    label_list = helper.load(name + "_label.sav")
    print("FEATURE:{} / LABEL:{}".format(feature_list.shape, len(label_list)))
    return train_test_split(
        feature_list,
        label_list,
        test_size=size)


def train(estimator, name="sample04", **args):
    time1 = DateUtils.current_time_millis()
    (train_data, test_data, train_label, test_label) = load_data(name, 0.3)
    # train_data = np.array(train_data)
    # train_label = np.array(train_label)
    time2 = DateUtils.current_time_millis()
    print("LOAD COMPLETE:{}ms".format(time2 - time1))
    # svc = SVC(
    #     kernel="linear")
    # svc = LinearSVC()
    tmp = estimator(**args)
    tmp.fit(train_data, train_label)
    helper.dump(tmp, name + "_model.sav")
    time1 = DateUtils.current_time_millis()
    print("TRAIN COMPLETE:{}ms".format(time1 - time2))
    score = tmp.score(test_data, test_label)
    time2 = DateUtils.current_time_millis()
    print("RESULT:{}({}: {}ms)".format(estimator.__name__, round(score, 6), time2 - time1))


def get_feature(item, name="sample04"):
    target = np.array([item])
    union: FeatureUnion = helper.load(name + "_vec.sav")
    # dvec: DictVectorizer = helper.load(name + "_dvec.sav")
    # # target = dvec.transform(target)
    # cvec: CountVectorizer = helper.load(name + "_cvec.sav")
    # # content = cvec.transform(content)
    # # TfidfTransformer().fit_transform(content)
    # union = FeatureUnion(
    #     transformer_list=[
    #         ("feature", Pipeline([
    #             ('selector', ItemSelector(1)),
    #             ("dvec", dvec)
    #         ])),
    #         ("content", Pipeline([
    #             ('selector', ItemSelector(0)),
    #             ('cvec', cvec),
    #             ('tfidf', TfidfTransformer())
    #         ]))
    #     ],
    #     transformer_weights={"feature": 1.0, "content": 1.0})
    return union.transform(target)


def to_sample(target: str):
    n = target[:1]
    age = NAMES.index(n) + 20 if n in NAMES else 30
    return get_feature([target, {"author": n + "_USER" if n in NAMES else "UNKNOWN", "age": age}])


def predict(set_feature, name="sample04"):
    model = helper.load(name + "_model.sav")
    return model.predict(set_feature)


if __name__ == "__main__":
    # create_feature("sample04")  # (400000, 259339)
    train(LinearSVC)  # LinearSVC(0.883067: 343532ms)
    # train(LogisticRegression)  # LogisticRegression(0.884467: 58500ms)
    # train(GaussianNB)  # GaussianNB(0.60735,4806)
    # train(KNeighborsClassifier, name="sample04_test")  #
    # train(RandomForestClassifier)  # RandomForestClassifier(0.814642: 1792755ms)
    # train(XGBClassifier)  # XGBClassifier(0.790492: 693539ms)
    sample = to_sample("works fine, but Maha Energy is better: Check out Maha Energy's website. Their Powerex MH-C204F charger works in 100 minutes for rapid charge, with option for slower charge (better for batteries). And they have 2200 mAh batteries.")
    result = predict(sample)
    print(result)
    # StratifiedShuffleSplit  # 交叉生成数据
    pass
