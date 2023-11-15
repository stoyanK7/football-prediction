def remove_collinear_features(df, threshold):
    """
    Removes collinear features in a dataframe with a correlation coefficient
    greater than the threshold. Removing collinear features can help a model
    to generalize and improves the interpretability of the model.

    Borrowed from https://www.kaggle.com/code/oldwine357/removing-highly-correlated-features

    :param df: features dataframe
    :param threshold: features with correlations greater than this value are removed
    :return: df: dataframe that contains only the non-highly-collinear features
    """

    # Calculate the correlation matrix.
    corr_matrix = df.corr()
    iters = range(len(corr_matrix.columns) - 1)
    drop_cols = []

    # Iterate through the correlation matrix and compare correlations.
    for i in iters:
        for j in range(i+1):
            item = corr_matrix.iloc[j:(j+1), (i+1):(i+2)]
            col = item.columns
            val = abs(item.values)

            # If correlation exceeds the threshold.
            if val >= threshold:
                drop_cols.append(col.values[0])

    # Drop one of each pair of correlated columns.
    drops = set(drop_cols)
    df = df.drop(columns=drops)
    print(f'Removed Columns {drops}')
    return df
