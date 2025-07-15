import json
import logging
import os
from math import isclose
from numbers import Number

import pandas as pd

# Set the level of logging
DEBUG = os.environ.get('DEBUG', False)
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


class Portfolio:
    def __init__(self, **kwargs):
        model = kwargs.get('model')

        if not isinstance(model, dict):
            error_msg = "Invalid model: model should be a dict"
            logging.error(error_msg)
            raise TypeError(error_msg)

        if not all(isinstance(value, (int, float)) for value in model.values()):
            error_msg = "Invalid model: values should be numeric"
            logging.error(error_msg)
            raise ValueError(error_msg)

        try:
            df = pd.DataFrame(model.items(), columns=['Asset', 'Weight'])
        except Exception as e:
            error_msg = f"Error creating DataFrame: {e}"
            logging.error(error_msg)
            raise

        # Add extensive logging for weight calculation
        logging.info("Model Weights:")
        for asset, weight in model.items():
            logging.info(f"{asset}: {weight}")

        total_weight = df.Weight.sum()
        logging.info(f"Total Weight Calculation:")
        logging.info(f"Sum of weights: {total_weight}")
        logging.info(f"DataFrame weights: {df['Weight'].tolist()}")

        # Use a more tolerant comparison
        if not isclose(total_weight, 1, rel_tol=1e-9, abs_tol=1e-9):
            error_msg = f"Sum of weights in the model not equal to 1. Total weight: {total_weight}"
            logging.error(error_msg)
            raise ValueError(error_msg)

        self.total_weight = total_weight
        self.model = df
        self.portfolio_value = None
        self.final_portfolio_value = None

    def get_current_value(self, values=None):
        current_value = {}

        if values is None:
            for asset in self.model['Asset']:
                current_value[asset] = float(input(f"Enter the current value for asset '{asset}': "))
        else:
            if len(values) != self.model.shape[0]:
                warning_msg = "Some current values were not provided, assuming $0"
                logging.warning(warning_msg)

            for asset in self.model['Asset']:
                current_value[asset] = values.get(asset, 0)

        if not all(isinstance(value, (int, float)) for value in current_value.values()):
            error_msg = "Invalid current values: values should be numeric"
            logging.error(error_msg)
            raise TypeError(error_msg)

        if any(value < 0 for value in current_value.values()):
            error_msg = "Invalid current values: all values should be greater than 0"
            logging.error(error_msg)
            raise ValueError(error_msg)

        self.model['CurrentValue'] = self.model['Asset'].map(current_value)
        self.portfolio_value = sum(self.model['CurrentValue'])

    def calc_current_mix(self, threshold=0.01):
        self.model['CurrentMix'] = self.model['CurrentValue'] / self.portfolio_value
        if not isclose(self.model['CurrentMix'].sum(), 1, rel_tol=threshold):
            raise ValueError(f"Sum of CurrentMix is not close to 1 (within tolerance): {self.model['FinalMix'].sum()}")

    def calc_delta_to_target(self, new_money=None):
        if new_money is None:
            new_money = 0

        if not isinstance(new_money, Number):
            error_msg = "Invalid type: new money should be a numeric type"
            logging.error(error_msg)
            raise TypeError(error_msg)

        if float(new_money) < 0.:
            error_msg = "Invalid value: new money should be 0 or more"
            logging.error(error_msg)
            raise ValueError(error_msg)

        self.model['DeltaToTarget'] = self.model['Weight'] - self.model['CurrentMix']
        self.model['AbsDeltaToTarget'] = self.model['DeltaToTarget'] * self.portfolio_value
        self.model['NewMoney'] = self.model['Weight'] * new_money
        self.model['Total'] = self.model['AbsDeltaToTarget'] + self.model['NewMoney']
        self.calculate_final_mix()
        self.model['Action'] = self.model['Total'].apply(lambda x: 'Buy' if x > 0 else 'Sell')

    def calculate_final_mix(self, threshold=0.01):
        self.model['FinalValue'] = self.model['CurrentValue'] + self.model['Total']

        self.final_portfolio_value = sum(self.model['FinalValue'])
        self.model['FinalMix'] = self.model['FinalValue'] / self.final_portfolio_value

        if not isclose(self.model['FinalMix'].sum(), 1, rel_tol=threshold):
            raise ValueError(f"Sum of FinalMix is not close to 1 (within tolerance): {self.model['FinalMix'].sum()}")

        diff = abs(self.model['FinalMix'] - self.model['Weight'])
        if any(diff > threshold):
            raise ValueError("Threshold exceeded between corresponding rows of columns.")

    def print_rebalancing_actions(self):
        columns_to_output = ['Asset', 'Weight', 'CurrentValue', 'CurrentMix', 'Total', 'Action']

        data = self.model[columns_to_output]

        logging.info('\n' + data.to_string(index=False))

        # Return as a string
        # return output

        # Return as a JSON object
        # return data.to_dict(orient='records')

        # Return as a dataframe
        # return data

    def print(self):
        logging.info('\n' + self.model.to_string(index=False))


def main(**kwargs):
    # Parse arguments. None if missing.
    model = kwargs.get('model')
    new_money = kwargs.get('new_money')
    values = kwargs.get('values')

    # Instantiate the portfolio object
    portfolio = Portfolio(model=model)

    # Get current values, or pass values as dict
    portfolio.get_current_value(values)

    # Execute calculations
    portfolio.calc_current_mix()
    portfolio.calc_delta_to_target(new_money)

    # Output results
    portfolio.print_rebalancing_actions()
    if DEBUG:
        portfolio.print()

    return portfolio.model


if __name__ == "__main__":
    test_json_model = '''
    {
      "Asset1": 0.20,
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    test_model = json.loads(test_json_model)
    test_new_money = 2000
    test_values = {'Asset1': 1000, 'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    result = main(model=test_model, new_money=test_new_money, values=test_values)
    output = result.to_dict(orient='records')
