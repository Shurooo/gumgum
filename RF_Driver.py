import RF_Wrapper as rfw


init_estimators = 40
add_estimators = 0
min_weight_fraction_leaf=0.00000001,
class_weight={0:1, 1:1000},
max_features="sqrt"

clf = rfw.RandomForsetWrapper(init_estimators,
                              add_estimators,
                              min_weight_fraction_leaf=min_weight_fraction_leaf,
                              class_weight=class_weight,
                              max_features=max_features)

clf.run_predict([(5, 1)], [(5, 2)])
