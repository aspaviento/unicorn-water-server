#!/usr/bin/env python3

import json
import math
import os
import threading
from datetime import datetime, timezone
from time import monotonic, sleep

from flask import Flask, jsonify, make_response, request, send_from_directory
from flask_cors import CORS
from jsmin import jsmin

from lib.unicorn_wrapper import UnicornWrapper

DISPLAY_WIDTH = 17
DISPLAY_HEIGHT = 7
DEFAULT_PORT = 9002

OFF = (0, 0, 0)
OUTLINE = (190, 235, 255)
TEXT_BLUE = (52, 178, 255)
TEXT_OVERFLOW = (255, 45, 64)
LOW_BLUE = (0, 72, 145)
MID_BLUE = (0, 132, 220)
HIGH_BLUE = (38, 186, 255)
FOAM = (182, 244, 255)

BUCKET_LEFT = 12
BUCKET_RIGHT = 16
BUCKET_INNER_LEFT = BUCKET_LEFT + 1
BUCKET_INNER_RIGHT = BUCKET_RIGHT - 1

DIGITS = {
    '0': ('111', '101', '101', '101', '111'),
    '1': ('010', '110', '010', '010', '111'),
    '2': ('111', '001', '111', '100', '111'),
    '3': ('111', '001', '111', '001', '111'),
    '4': ('101', '101', '111', '001', '001'),
    '5': ('111', '100', '111', '001', '111'),
    '6': ('111', '100', '111', '101', '111'),
    '7': ('111', '001', '010', '010', '010'),
    '8': ('111', '101', '111', '101', '111'),
    '9': ('111', '101', '111', '001', '111'),
}

hardware_lock = threading.RLock()
animation_thread = None
unicorn = UnicornWrapper()
width, height = unicorn.getShape()
if (width, height) != (DISPLAY_WIDTH, DISPLAY_HEIGHT):
    raise RuntimeError(
        f'Unicorn Water Server requires a 17x7 display, got {width}x{height}. '
        'Use a Unicorn HAT Mini at rotation 0.'
    )

state = {
    'liters': 0,
    'displayLiters': 0,
    'overflow': False,
    'activeRows': 0,
    'displayMode': 'water',
    'lastCalled': None,
    'lastCalledApi': None,
}


class WaterFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                start_rainbow()
        super().run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = WaterFlaskApp(__name__, static_folder='frontend/build', static_url_path='/')
CORS(app, resources={r'/api/*': {'origins': '*'}})


def read_json_body():
    raw = request.get_data(as_text=True) or '{}'
    try:
        content = json.loads(jsmin(raw))
    except ValueError:
        return None, make_response(jsonify({'error': 'Invalid JSON body'}), 400)
    if not isinstance(content, dict):
        return None, make_response(jsonify({'error': 'JSON body must be an object'}), 400)
    return content, None


def validate_number(content, field, minimum, maximum, default):
    value = content.get(field, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None, f'{field} must be a number'
    if value < minimum or value > maximum:
        return None, f'{field} must be between {minimum} and {maximum}'
    return value, None


def validate_liters(content):
    value = content.get('liters')
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None, 'liters must be a number'
    if not math.isfinite(value) or value < 0:
        return None, 'liters must be a non-negative finite number'
    return int(value), None


def display_liters(liters):
    return min(999, max(0, int(liters)))


def is_overflow(liters):
    return int(liters) > 999


def active_rows(liters):
    if liters <= 0:
        return 0
    return min(5, ((liters - 1) // 200) + 1)


def update_water_state(liters):
    state['liters'] = int(liters)
    state['displayLiters'] = display_liters(liters)
    state['overflow'] = is_overflow(liters)
    state['activeRows'] = active_rows(liters)


def set_pixel(x, y, color):
    if 0 <= x < width and 0 <= y < height:
        unicorn.setPixel(x, y, *color)


def draw_number(liters, overflow=False):
    value = f'{int(liters):>3}'
    color = TEXT_OVERFLOW if overflow else TEXT_BLUE
    for digit_index, digit in enumerate(value):
        if digit == ' ':
            continue
        x_offset = digit_index * 4
        for y, row in enumerate(DIGITS[digit]):
            for x, cell in enumerate(row):
                if cell == '1':
                    set_pixel(x_offset + x, y + 1, color)


def draw_bucket(rows, wave_phase=0):
    for x in range(BUCKET_LEFT, BUCKET_RIGHT + 1):
        set_pixel(x, DISPLAY_HEIGHT - 1, OUTLINE)
    for y in range(1, DISPLAY_HEIGHT):
        set_pixel(BUCKET_LEFT, y, OUTLINE)
        set_pixel(BUCKET_RIGHT, y, OUTLINE)

    if rows == 0:
        return

    filled_rows = set(range(DISPLAY_HEIGHT - 2, DISPLAY_HEIGHT - 2 - rows, -1))
    surface_y = min(filled_rows)
    for x in range(BUCKET_INNER_LEFT, BUCKET_INNER_RIGHT + 1):
        shimmer = ((x + int(wave_phase)) % 4) == 0
        for y in filled_rows:
            if y == surface_y:
                color = FOAM if shimmer else HIGH_BLUE
            elif y >= DISPLAY_HEIGHT - 3:
                color = LOW_BLUE
            else:
                color = MID_BLUE
            set_pixel(x, y, color)


def render_display(wave_phase=0):
    update_water_state(state['liters'])
    with hardware_lock:
        unicorn.clear()
        unicorn.setBrightness(0.5)
        draw_number(state['displayLiters'], state['overflow'])
        draw_bucket(state['activeRows'], wave_phase)
        unicorn.show()


def stop_animation():
    global animation_thread
    if animation_thread is not None:
        animation_thread.do_run = False
        if animation_thread != threading.current_thread():
            animation_thread.join(timeout=1)
        animation_thread = None


def sleep_while_running(thread, seconds):
    end = monotonic() + seconds
    while getattr(thread, 'do_run', True):
        remaining = end - monotonic()
        if remaining <= 0:
            return
        sleep(min(0.05, remaining))


def display_rainbow(brightness, speed):
    current_thread = threading.current_thread()
    offset = 30
    frame = 0.0
    while getattr(current_thread, 'do_run', True):
        frame += 0.3
        with hardware_lock:
            unicorn.setBrightness(brightness)
            for x in range(DISPLAY_WIDTH):
                for y in range(DISPLAY_HEIGHT):
                    red = (math.cos((x + frame) / 2.0) + math.cos((y + frame) / 2.0)) * 64.0 + 128.0
                    green = (math.sin((x + frame) / 1.5) + math.sin((y + frame) / 2.0)) * 64.0 + 128.0
                    blue = (math.sin((x + frame) / 2.0) + math.cos((y + frame) / 1.5)) * 64.0 + 128.0
                    set_pixel(
                        x,
                        y,
                        tuple(int(max(0, min(255, color + offset))) for color in (red, green, blue)),
                    )
            unicorn.show()
        sleep_while_running(current_thread, speed)


def display_water_wave(speed):
    current_thread = threading.current_thread()
    wave_phase = 0
    while getattr(current_thread, 'do_run', True):
        render_display(wave_phase)
        wave_phase = (wave_phase + 1) % 4
        sleep_while_running(current_thread, speed)


def start_rainbow(brightness=1, speed=0.1):
    global animation_thread
    stop_animation()
    state['displayMode'] = 'rainbow'
    animation_thread = threading.Thread(target=display_rainbow, args=(brightness, speed), daemon=True)
    animation_thread.do_run = True
    animation_thread.start()


def start_water_display(speed=0.32):
    global animation_thread
    stop_animation()
    state['displayMode'] = 'water'
    animation_thread = threading.Thread(target=display_water_wave, args=(speed,), daemon=True)
    animation_thread.do_run = True
    animation_thread.start()


def switch_off():
    stop_animation()
    state['displayMode'] = 'off'
    with hardware_lock:
        unicorn.clear()
        unicorn.off()


def touch(endpoint):
    state['lastCalledApi'] = endpoint
    state['lastCalled'] = datetime.now(timezone.utc).isoformat()


def status_payload():
    return {
        **state,
        'height': height,
        'rotation': unicorn.getRotation(),
        'width': width,
        'unicorn': unicorn.getType(),
    }


@app.route('/', methods=['GET'])
def root():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/', methods=['GET'])
def api_index():
    return jsonify({
        'endpoints': {
            'off': {'methods': ['GET', 'POST'], 'path': '/api/off'},
            'rainbow': {'methods': ['POST'], 'path': '/api/rainbow'},
            'status': {'methods': ['GET'], 'path': '/api/status'},
            'water': {'methods': ['POST'], 'path': '/api/water'},
        }
    })


@app.route('/api/water', methods=['POST'])
def api_water():
    content, error_response = read_json_body()
    if error_response is not None:
        return error_response
    liters, error = validate_liters(content)
    if error:
        return make_response(jsonify({'error': error}), 400)
    update_water_state(liters)
    touch('/api/water')
    start_water_display()
    return jsonify(status_payload())


@app.route('/api/off', methods=['GET', 'POST'])
def api_off():
    touch('/api/off')
    switch_off()
    return jsonify(status_payload())


@app.route('/api/rainbow', methods=['POST'])
def api_rainbow():
    content, error_response = read_json_body()
    if error_response is not None:
        return error_response
    brightness, error = validate_number(content, 'brightness', 0, 1, 1)
    if error:
        return make_response(jsonify({'error': error}), 400)
    speed, error = validate_number(content, 'speed', 0.01, 60, 0.1)
    if error:
        return make_response(jsonify({'error': error}), 400)
    touch('/api/rainbow')
    start_rainbow(brightness, speed)
    return jsonify(status_payload())


@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify(status_payload())


@app.errorhandler(404)
def not_found(_error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('UNICORN_WATER_PORT', DEFAULT_PORT)), debug=False)
