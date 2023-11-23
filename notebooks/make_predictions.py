import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import precision_score


def make_predictions(data, predictors, cutoff_date='2023-04-01'):
    """
    Make predictions using the random forest classifier.

    :param data: the dataframe to use
    :param predictors: the predictor columns
    :param cutoff_date: the date to split the data on
    :return: combined: a dataframe containing the actual and predicted values
    """
    # Split the data into train and test sets.
    train_set = data[data['date'] < cutoff_date]
    test_set = data[data['date'] >= cutoff_date]
    print(f'Train: {len(train_set)} matches ({len(train_set) / len(data):.2%})')
    print(f'Test: {len(test_set)} matches ({len(test_set) / len(data):.2%})')

    # Create and fit (train) the model.
    model = HistGradientBoostingClassifier()
    model.fit(train_set[predictors], train_set['target'])

    # Make predictions on the test dataset and calculate the precision score.
    predictions = model.predict(test_set[predictors])
    precision = precision_score(test_set['target'], predictions)
    print(f'Precision: {precision:.2%}')

    # Create a dataframe containing the actual and predicted values.
    combined = pd.DataFrame(
        dict(actual=test_set['target'], prediction=predictions),
        index=test_set.index,
    )
    return combined
