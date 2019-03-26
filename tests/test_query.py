import pytest

from hseling_api_direct_speech.query import query_data


test_data = [([],[])
]


@pytest.mark.parametrize("input_data, expected_result", test_data)
def test_process_data(input_data, expected_result):
    result = input_data
    assert result == expected_result
