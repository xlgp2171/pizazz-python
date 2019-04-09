"""字典特征提取器，特征向量化"""
import csv
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import SVC

from piz_base import PathUtils, IOUtils
from piz_ml.skl import helper


def read_dataset(resource):
    feature_list = []
    label_list = []
    path = PathUtils.to_file_path(__file__, "data", resource)
    with IOUtils.get_resource_as_stream(path) as f:
        reader = csv.reader(f)
        headers = next(reader)

        for row in reader:
            label_list.append(row[-1])
            row_dic = {}

            for i, item in enumerate(row[:-1]):
                row_dic[headers[i]] = item
            feature_list.append(row_dic)
    return feature_list, label_list


def train_and_test_data(feature_list, label_list):
    size = int(0.7 * len(feature_list))
    train_data = feature_list[:size]
    train_label = label_list[:size]
    test_data = feature_list[size:]
    test_label = label_list[size:]
    return train_data, train_label, test_data, test_label


def train_and_test(name):
    (feature_list, label_list) = read_dataset(name + ".csv")
    # feature_list = feature_list[0:2]
    # print(feature_list)
    # 字典向量生成器
    vec = DictVectorizer(
        sparse=False)
    # 转换
    feature_list = vec.fit_transform(feature_list)
    # print(feature_list)
    # print(vec.get_feature_names())
    helper.dump(vec, name + "_data.sav")
    vec.get_feature_names()
    #
    # le = LabelEncoder()
    # label_list = le.fit_transform(label_list)
    # dump(le, name + "_label.sav")
    #
    # (train_data, train_label, test_data, test_label) = train_and_test_data(feature_list, label_list)
    (train_data, train_label, test_data, test_label) = train_test_split(
        feature_list,
        label_list,
        test_size=0.3)
    svm = SVC(
        kernel='linear')
    svm.fit(train_data, train_label)
    helper.dump(svm, name + "_model.sav")
    #
    # svm = load(name + "_model.sav")
    result = svm.score(test_data, test_label)
    print(result)


def to_sample(name, target):
    vec = helper.load(name + "_data.sav")
    feature_names = vec.get_feature_names()
    sample_source = [k + "=" + v for k, v in target.items()]
    sample_test = np.zeros(len(feature_names))

    for i in sample_source:
        if i in feature_names:
            sample_test[feature_names.index(i)] = 1.0
    return sample_test


def predict(name, target):
    tmp = to_sample(name, target)
    svm = helper.load(name + "_model.sav")
    result = svm.predict([tmp])
    print(result)


if __name__ == '__main__':
    # 训练
    # train_and_test("sample01")
    sample = {'要求服务类型': '维修', '实际服务类型': '换机', '实际服务方式': '双程拉送', '对象码': '23D',
              '对象': '观察窗总成', '故障现象码': '654', '故障原因码': 'B8', '维修措施编码': 'ZL', '维修措施': '换机'}
    # 预测
    predict("sample01", sample)
