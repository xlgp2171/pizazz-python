""""""
import logging
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from piz_ml.skl import helper
from piz_ml.skl.Test04 import read_dataset

logger = logging.getLogger(__name__)


class ItemSelector(BaseEstimator, TransformerMixin):
    def __init__(self, index):
        self.index = index

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[:, self.index]


class SVMOperator(object):
    NAMES = [t for t in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]

    def __init__(self, name):
        self.name = name
        self.model = helper.load(name + "_model.sav")

    def get_feature(self, item):
        target = np.array([item])
        union = helper.load(self.name + "_vec.sav")
        return union.transform(target)

    def to_feature(self, target):
        n = target[:1]
        age = self.NAMES.index(n) + 20 if n in self.NAMES else 30
        return self.get_feature([target, {"author": n + "_USER" if n in self.NAMES else "UNKNOWN", "age": age}])

    def _predict(self, feature):
        return self.model.predict(feature)

    def predict(self, target: str):
        feature = self.to_feature(target)
        return self.model.predict(feature)


if __name__ == "__main__":
    (data, label) = read_dataset("sample04_test")
    svm = SVMOperator("sample04")

    for i in data:
        result = svm.predict(i[0])
        print(result)
    pass
