class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data


def get_valid_response():
    return MockResponse(200, {'success': True})


def get_valid_account_response(credits: int = 300):
    return MockResponse(200, {
        'plan': [
            {
                'type': 'free',
                'credits': credits,
                'creditsType': 'sendLimit'
            },
            {
                'type': 'sms',
                'credits': 0,
                'creditsType': 'sendLimit'
            }
        ],
    })
