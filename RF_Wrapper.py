from sklearn.ensemble import RandomForestClassifier
import Get_Data as gd
import Predict_Module as predm
import Test_Module as testm


class RandomForsetWrapper:
    def __init__(self,
                 init_estimators,
                 add_estimators,
                 min_weight_fraction_leaf=0.,
                 class_weight=None,
                 max_features="auto",
                 oob_score=False,
                 n_jobs=-1,
                 random_state=1514):
        self.init_estimators = init_estimators
        self.add_estimators = add_estimators
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.class_weight = class_weight
        self.max_features = max_features

        n_estimators = init_estimators - add_estimators
        if add_estimators == 0:
            warm_start = False
        else:
            warm_start = True
        self.clf = RandomForestClassifier(n_estimators=n_estimators,
                                          min_weight_fraction_leaf=min_weight_fraction_leaf,
                                          class_weight=class_weight,
                                          max_features=max_features,
                                          oob_score=oob_score,
                                          warm_start=warm_start,
                                          n_jobs=n_jobs,
                                          random_state=random_state)

    def train(self, addr_in, sampling_ratio, sampling_mode):
        X, y = gd.get(addr_in, ratio=sampling_ratio, mode=sampling_mode)
        self.clf.n_estimators += self.add_estimators
        self.clf.fit(X, y)

    def train_online(self, addr_in, sampling_ratio, sampling_mode):
        self.train(addr_in, sampling_ratio, sampling_mode)

    def test(self, addr_in):
        X, y = gd.get(addr_in)
        prediction = self.clf.predict(X)
        return y, prediction

    def run_predict(self, data_train, data_test, sampling="None"):
        predm.run(self, data_train, data_test, sampling)

    def run_test(self,
                 data,
                 sampling_ratio=2.65,
                 sampling_mode="normal",
                 train_test_mode=-1,
                 on_off_line="Online",
                 report_name=-1,
                 report_root="/home/ubuntu/Weiyi/Reports"):
        if train_test_mode == -1:
            train_test_mode = ["Next_day"]

        param = []
        param.append("sampling ratio = {}".format(sampling_ratio))
        param.append("sampling mode = {}".format(sampling_mode))
        param.append("init_estimators = {}".format(self.init_estimators))
        param.append("add_estimators = {}".format(self.add_estimators))
        param.append("min_weight_fraction_leaf = {}".format(self.min_weight_fraction_leaf))
        param.append("class weight = {}".format(str(self.class_weight)))
        param.append(("max_features = {}".format(self.max_features)))

        testm.run(self, "RF", data, sampling_ratio, sampling_mode, train_test_mode, on_off_line, param, report_name, report_root)
