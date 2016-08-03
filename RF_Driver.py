import RF_Wrapper as rfw


clf = rfw.RandomForsetWrapper(init_estimators=40,
                              add_estimators=20,
                              class_weight={0:1, 1:8.5},
                              min_weight_fraction_leaf=0.00001,
                              max_features="sqrt")

# clf.run_predict(data_train=[(6, 19)], data_test=[(6, 20)], sampling_ratio=1.4, sampling_mode="normal")
clf.run_test([[(6, i) for i in range(4, 11)]], sampling_ratio=1.4, report_name="RF_Test.xlsx")
