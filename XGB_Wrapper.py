import numpy as np
import xgboost as xgb
from sklearn import metrics


class XGBWrapper:
    def __init__(self, param, num_round, verbose_eval):
        self.param = param
        self.num_round = num_round
        self.verbose_eval = verbose_eval
        self.bst = None
        self.feature_importances_ = []

    def fit(self, X, y):
        data_train = xgb.DMatrix(X, label=y)
        self.bst = xgb.train(self.param, data_train, self.num_round, verbose_eval=self.verbose_eval)
        importances = [0]*np.size(X, 1)
        for item in self.bst.get_fscore().iteritems():
            importances[int(item[0][1:])] = item[1]
        self.feature_importances_ = np.array(importances)

    def score(self, X, y):
        data_test = xgb.DMatrix(X, label=y)
        prob = self.bst.predict(data_test)
        score = 0
        for cutoff in range(10, 15):
            cut = cutoff/float(100)   # Cutoff in decimal form
            y_pred = prob > cut   # If y values are greater than the cutoff
            recall = metrics.recall_score(y, y_pred)
            filter_rate = sum(np.logical_not(y_pred))/float(len(prob))
            if recall*6.7+filter_rate > score:
                score = recall*6.7+filter_rate
        return score

    def get_params(self, deep):
        param_dict = {"param": self.param, "num_round":self.num_round, "verbose_eval":self.verbose_eval}
        return param_dict

    def predict_prob(self, X):
        data_test = xgb.DMatrix(X)
        return self.bst.predict(data_test)
