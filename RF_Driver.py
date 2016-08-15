import RF_Wrapper as rfw


clf = rfw.RandomForsetWrapper(init_estimators=40,
                              add_estimators=20,
                              class_weight={0:1, 1:8.5},
                              min_weight_fraction_leaf=0.000006,
                              max_features="sqrt")

# clf.run_predict(data_train=[(6, 4)], data_test=[(6, 5)], sampling_ratio=1.4, sampling_mode="normal")
clf.run_test([[(6, i) for i in range(4, 26)]], sampling_ratio=1.4, report_name="RF_Test.xlsx")
