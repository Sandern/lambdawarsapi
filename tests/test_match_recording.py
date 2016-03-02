from flask import json
from datetime import datetime
from .flask_test_base import FlaskrTestCase

class MatchRecordingTestCase(FlaskrTestCase):
    def test_landing_url(self):
        rv = self.app.get('/')
        assert b'Lambda Wars API' in rv.data

    def test_invalid_start_match_no_params(self):
        response = self.app.post('/matches/record_start')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertEqual(data['success'], False, msg='expect failure due missing json body')

    def test_start_record_match(self):
        response = self.app.post('/matches/record_start', data=json.dumps({
                'mode': 'annihilation',
                'map': 'hlw_woodland',
                'type': '2vs2',
                'start_date': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                'players': {"9": {"name": "CPU #4", "color": "#ff0000"}, "4": {"name": "Sandern", "color": "#c87814", "steamid": "STEAM_0:0:3833324"}},
            }),
            content_type='application/json',
            environ_base={'REMOTE_ADDR': '127.0.0.1'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertEqual(data['success'], True, msg=data)
