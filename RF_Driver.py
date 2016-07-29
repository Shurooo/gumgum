import RF_Wrapper as rfw


clf = rfw.RandomForsetWrapper(init_estimators=10,
                              add_estimators=0,
                              max_features="sqrt",
                              min_weight_fraction_leaf=0.0000001,
                              class_weight={0:1, 1:100})

clf.run_predict([(5, 1)], [(5, 2)], sampling="Over")
