import RF_Wrapper as rfw


clf = rfw.RandomForsetWrapper(init_estimators=40,
                              add_estimators=10,
                              max_features="sqrt",
                              min_weight_fraction_leaf=0.00001,
                              class_weight={0:1, 1:100})

clf.run_test([[(6, i) for i in range(4, 11)]], sampling_ratio=-1, report_name="RF_Test.xlsx")
