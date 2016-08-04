import xgboost as xgb


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
        self.feature_importances_ = self.bst.get_fscore()

    def score(self):
        return self.bst.get_fscore()

    def get_params(self, deep):
        param_dict = {"param": self.param, "num_round":self.num_round, "verbose_eval":self.verbose_eval}
        return param_dict
