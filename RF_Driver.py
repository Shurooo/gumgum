import RF_Wrapper as rfw


clf = rfw.RandomForsetWrapper(init_estimators=300,
                              add_estimators=0,
                              max_features="sqrt",
                              min_weight_fraction_leaf=0.00001,
                              class_weight={0:1, 1:100})

clf.run_predict([(6, 4)], [(6, 5)], sampling="Over")
