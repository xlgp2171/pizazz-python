"""保存一般模型"""
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline, FeatureUnion

from piz_ml.skl import helper
from piz_ml.skl.Test04 import read_dataset, ItemSelector

if __name__ == "__main__":
    (feature_list, label_list) = read_dataset("sample04_test")
    feature_list = np.array(feature_list)
    stop_words = helper.read_stopwords()
    # feature_list = feature_list[:, 0]
    #
    union = FeatureUnion(
        transformer_list=[
            ("feature", Pipeline([
                ('selector', ItemSelector(1)),
                ("vec", DictVectorizer(
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
    union.fit_transform(feature_list)
    pipe: Pipeline = union.transformer_list[1][1]
    cvec: CountVectorizer = pipe.named_steps["cvec"]
    arr = cvec.get_feature_names()
    name = union.get_feature_names()
    print(name)
