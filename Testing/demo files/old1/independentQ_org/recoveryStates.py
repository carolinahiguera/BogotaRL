
centros =pd.read_csv('./states/recoveryStates_agt0.csv', sep=' ', skipinitialspace=True, header=None)
centros = centros.values


observation = np.array([0, 0, 8.17, 22.3, 8.46, 10.1])
res = np.linalg.norm(observation.T-centros, axis=1, ord=2)
state = np.argmin(res)
