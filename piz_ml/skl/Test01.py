""""""
import csv
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import SVC

from piz_base import PathUtils, IOUtils


def read_dataset(resource):
    feature_list = []
    label_list = []
    path = PathUtils.to_file_path(__file__, "data", resource)
    with IOUtils.get_resource_as_stream(path, "r") as f:
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


def dump(obj, resource):
    path = PathUtils.to_file_path(__file__, "model", resource)
    pickle.dump(obj, IOUtils.get_resource_as_stream(path, "wb"))


def train_and_test(name):
    (feature_list, label_list) = read_dataset(name + ".csv")
    (train_data, train_label, test_data, test_label) = train_and_test_data(feature_list, label_list)
    print("{}\n{}".format(train_data[16], train_label[16]))
    # feature_list = feature_list[0:2]
    # 字典向量生成器
    vec = DictVectorizer(
        sparse=False)
    # 安装 转换
    dummy_x = vec.fit_transform(train_data)
    # 保存特征
    dump(vec, name + "_data.sav")
    #
    le = LabelEncoder()
    dummy_y = le.fit_transform(train_label)
    dump(le, name + "_label.sav")
    #
    svm = SVC(
        kernel='linear')
    svm.fit(dummy_x, dummy_y)
    dump(svm, name + "_model.sav")
    #
    dummy_x2 = DictVectorizer(
        sparse=False).fit_transform(test_data)
    dummy_y2 = LabelEncoder().fit_transform(test_label)
    result = svm.score(dummy_x2, dummy_y2)
    print(result)


if __name__ == '__main__':
    # set_svm: SVC =
    train_and_test("sample01")
    # result = svm.predict({'要求服务类型': '维修', '实际服务类型': '换机', '实际服务方式': '双程拉送', '对象码': '316', '对象': '电脑板', '故障现象码': '111', '故障原因码': 'NN', '维修措施编码': 'ZL', '维修措施': '换机'})
    # print(result)
