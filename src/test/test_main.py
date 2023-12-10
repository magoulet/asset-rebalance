import json
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from lambda_logic.main import main
from unittest.mock import patch


def test_function_with_valid_inputs():
    json_model = '''
    {
      "Asset1": 0.2,
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)
    new_money = 2000
    values = {'Asset1': 1000, 'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    result = main(model=model, new_money=new_money, values=values)

    expected_df = pd.read_csv('fixtures/valid_data_expected_output.csv')

    assert_frame_equal(result, expected_df)


def test_empty_model():
    new_money = 0
    values = {'Asset1': 1000, 'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    with pytest.raises(TypeError) as error:
        main(new_money=new_money, values=values)

    assert str(error.value) == "Invalid model: model should be a dict"


def test_invalid_model():
    json_model = '''
    {
      "Asset1": "abc",
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)
    new_money = 0
    values = {'Asset1': 1000, 'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    with pytest.raises(ValueError) as error:
        main(model=model, new_money=new_money, values=values)

    assert str(error.value) == "Invalid model: values should be numeric"

    json_model = '''
    {
      "Asset1": "",
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)

    with pytest.raises(ValueError) as error:
        main(model=model, new_money=new_money, values=values)

    assert str(error.value) == "Invalid model: values should be numeric"


def test_model_weight_not_equal_1():
    json_model = '''
    {
      "Asset1": 0.5,
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)
    new_money = 0
    values = {'Asset1': 1000, 'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    with pytest.raises(ValueError) as error:
        main(model=model, new_money=new_money, values=values)
    
    assert str(error.value) == "Sum of weights in the model not equal to 1."


def test_empty_new_money():
    json_model = '''
    {
      "Asset1": 0.2,
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)
    values = {'Asset1': 1000, 'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    result = main(model=model, values=values)

    expected_df = pd.read_csv('fixtures/empty_new_money_expected_output.csv')

    assert_frame_equal(result, expected_df)


def test_invalid_new_money():
    json_model = '''
    {
      "Asset1": 0.2,
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)
    new_money = 'abc'
    values = {'Asset1': 1000, 'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    with pytest.raises(TypeError) as error:
        main(model=model, new_money=new_money, values=values)
    
    assert str(error.value) == "Invalid type: new money should be a numeric type"


def test_negative_new_money():
    json_model = '''
    {
      "Asset1": 0.2,
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)
    new_money = -2000
    values = {'Asset1': 1000, 'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    with pytest.raises(ValueError) as error:
        main(model=model, new_money=new_money, values=values)
    
    assert str(error.value) == "Invalid value: new money should be 0 or more"


def test_empty_current_values():
    json_model = '''
    {
      "Asset1": 0.2,
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)
    new_money = 2000

    with patch('builtins.input') as mock_input:
        main(model=model, new_money=new_money)
    
        mock_input.assert_called()


def test_missing_current_values():
    json_model = '''
    {
      "Asset1": 0.2,
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)
    new_money = 2000
    values = {'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    result = main(model=model, new_money=new_money, values=values)

    expected_df = pd.read_csv('fixtures/missing_current_value_expected_output.csv')

    assert_frame_equal(result, expected_df)


def test_invalid_current_values():
    json_model = '''
    {
      "Asset1": 0.2,
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)
    new_money = 2000
    values = {'Asset1': 'abc', 'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    with pytest.raises(TypeError) as error:
        main(model=model, new_money=new_money, values=values)
    
    assert str(error.value) == "Invalid current values: values should be numeric"


def test_negative_current_values():
    json_model = '''
    {
      "Asset1": 0.2,
      "Asset2": 0.15,
      "Asset3": 0.15,
      "Asset4": 0.5
    }
    '''
    model = json.loads(json_model)
    new_money = 2000
    values = {'Asset1': -1000, 'Asset2': 1000, 'Asset3': 1000, 'Asset4': 1000}

    with pytest.raises(ValueError) as error:
        main(model=model, new_money=new_money, values=values)
    
    assert str(error.value) == "Invalid current values: all values should be greater than 0"
