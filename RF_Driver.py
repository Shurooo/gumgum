import RF_Wrapper as rfw


clf = rfw.RandomForsetWrapper(init_estimators=40,
                              add_estimators=0,
                              class_weight={0:1, 1:5},
                              min_weight_fraction_leaf=0.000005,
                              max_features="sqrt")

clf.run_test([[(6, i) for i in range(4, 11)]], sampling_ratio=2.6, sampling_mode="res-25", report_name="RF_Test.xlsx")
