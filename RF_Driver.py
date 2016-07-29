import RF_Wrapper as rfw


init_estimators = 40
add_estimators = 0
min_weight_fraction_leaf=0.00000001,
class_weight={0:1, 1:1000},
max_features="sqrt"

clf = rfw.RandomForsetWrapper(init_estimators,
                              add_estimators,
                              class_weight={0:1, 1:100})

clf.run_predict([(5, 1)], [(5, 2)])
