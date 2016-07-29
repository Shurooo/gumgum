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
                 oob_score=True,
                 n_jobs=-1,
                 random_state=1514):
        self.add_estimators = add_estimators
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


    def train(self, addr_in, sampling):
        X, y = gd.get(addr_in, sampling=sampling)
        self.clf.n_estimators += self.add_estimators
        self.clf.fit(X, y)

    def train_online(self, addr_in, sampling):
        self.train(addr_in, sampling)

    def test(self, addr_in):
        X, y = gd.get(addr_in)
        prediction = self.clf.predict(X)
        return y, prediction

    def run_predict(self, data_train, data_test, sampling="None"):
        predm.run(self, data_train, data_test, sampling)

    def run_test(self,
                 data,
                 train_test_mode=-1,
                 on_off_line="Online",
                 report_name=-1,
                 report_root="/home/ubuntu/Weiyi/Reports"):
        if train_test_mode == -1:
            train_test_mode = ["day"]
        testm.run(self, data, train_test_mode, on_off_line, report_name, report_root)
