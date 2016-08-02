import RF_Wrapper as rfw


clf = rfw.RandomForsetWrapper(init_estimators=400,
                              add_estimators=0,
                              max_features="sqrt")


clf.run_predict(data_train=[(6, 4)], data_test=[(6, 5)], sampling_ratio=2.6, sampling_mode="normal")
# clf.run_test([[(6, i) for i in range(4, 11)]], sampling_ratio=2.6, sampling_mode="normal", report_name="RF_Test.xlsx")
