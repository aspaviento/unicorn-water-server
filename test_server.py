import unittest
from unittest.mock import patch

import server
from lib import unicorn_wrapper


class WaterServerTest(unittest.TestCase):
    def setUp(self):
        self.client = server.app.test_client()
        server.stop_animation()
        server.state.update({
            'liters': 0,
            'activeRows': 0,
            'displayMode': 'water',
        })
        server.render_display()

    def tearDown(self):
        server.stop_animation()

    def post_water(self, liters):
        return self.client.post('/api/water', json={'liters': liters})

    def test_liter_ranges_activate_expected_bucket_rows(self):
        expected = {
            0: 0,
            1: 1,
            199: 1,
            200: 1,
            201: 2,
            400: 2,
            401: 3,
            600: 3,
            601: 4,
            800: 4,
            801: 5,
            999: 5,
        }
        for liters, rows in expected.items():
            with self.subTest(liters=liters):
                response = self.post_water(liters)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json['activeRows'], rows)
                self.assertEqual(response.json['liters'], liters)

    def test_rejects_invalid_water_values(self):
        self.assertEqual(self.post_water(-1).status_code, 400)
        self.assertEqual(self.post_water(1000).status_code, 400)
        self.assertEqual(self.client.post('/api/water', json={'liters': True}).status_code, 400)
        self.assertEqual(self.client.post('/api/water', json={'value': 30}).status_code, 400)

    def test_status_reports_water_state_and_display_contract(self):
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['width'], 17)
        self.assertEqual(response.json['height'], 7)
        self.assertEqual(response.json['rotation'], 0)
        self.assertEqual(response.json['displayMode'], 'water')
        self.assertEqual(response.json['activeRows'], 0)

    def test_api_index_lists_water_endpoints_only(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        endpoints = response.json['endpoints']
        self.assertEqual(endpoints['water']['path'], '/api/water')
        self.assertEqual(endpoints['off']['path'], '/api/off')
        self.assertEqual(endpoints['rainbow']['path'], '/api/rainbow')
        self.assertEqual(endpoints['status']['path'], '/api/status')
        self.assertNotIn('battery', endpoints)
        self.assertNotIn('tariff', endpoints)
        self.assertNotIn('solaredgeInterface', endpoints)

    def test_water_pattern_uses_number_left_gap_and_bucket_right(self):
        server.state['liters'] = 830
        server.render_display()
        for x in range(0, server.BUCKET_LEFT):
            self.assertEqual(server.unicorn.pixels[x][0], server.OFF)
            if x != 11:
                self.assertNotEqual(server.unicorn.pixels[x][1], server.OUTLINE)
            self.assertEqual(server.unicorn.pixels[x][6], server.OFF)
        for y in range(server.DISPLAY_HEIGHT):
            self.assertEqual(server.unicorn.pixels[11][y], server.OFF)
        self.assertEqual(server.unicorn.pixels[0][1], server.TEXT_BLUE)
        self.assertEqual(server.unicorn.pixels[server.BUCKET_LEFT][6], server.OUTLINE)
        self.assertEqual(server.unicorn.pixels[server.BUCKET_RIGHT][6], server.OUTLINE)
        self.assertNotEqual(server.unicorn.pixels[server.BUCKET_INNER_LEFT][1], server.OFF)

    def test_off_turns_off_every_pixel(self):
        self.post_water(830)
        response = self.client.post('/api/off')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['displayMode'], 'off')
        self.assertTrue(all(
            server.unicorn.pixels[x][y] == server.OFF
            for x in range(server.DISPLAY_WIDTH)
            for y in range(server.DISPLAY_HEIGHT)
        ))

    def test_rainbow_starts_and_water_update_stops_animation(self):
        response = self.client.post('/api/rainbow', json={'brightness': 0.8, 'speed': 0.01})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['displayMode'], 'rainbow')
        self.assertIsNotNone(server.animation_thread)

        response = self.post_water(30)
        self.assertEqual(response.json['displayMode'], 'water')
        self.assertIsNotNone(server.animation_thread)
        self.assertEqual(server.animation_thread._target, server.display_water_wave)

    def test_rainbow_rejects_invalid_values(self):
        self.assertEqual(self.client.post('/api/rainbow', json={'brightness': 2}).status_code, 400)
        self.assertEqual(self.client.post('/api/rainbow', json={'speed': 0}).status_code, 400)

    def test_display_contract_is_native_unicorn_hat_mini_shape(self):
        self.assertEqual((server.width, server.height), (17, 7))
        self.assertEqual((server.DISPLAY_WIDTH, server.DISPLAY_HEIGHT), (17, 7))


class FakeMini:
    def __init__(self):
        self.rotation = None

    def set_brightness(self, _brightness):
        pass

    def set_rotation(self, rotation):
        self.rotation = rotation

    def get_shape(self):
        return (17, 7)


class UnicornWrapperTest(unittest.TestCase):
    def test_mini_uses_native_horizontal_rotation(self):
        with patch.object(unicorn_wrapper, 'UnicornHATMini', FakeMini):
            wrapper = unicorn_wrapper.UnicornWrapper('mini')
        self.assertEqual(wrapper.getHat().rotation, 0)
        self.assertEqual(wrapper.getShape(), (17, 7))


if __name__ == '__main__':
    unittest.main()
