import html
import os
import sys
import threading

import flask
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room

from lyrics_launcher import run_launcher

app = Flask('lyrics')
socketio = SocketIO(app)


if hasattr(sys, '_MEIPASS'):
    root_dir = sys._MEIPASS
else:
    root_dir = os.path.dirname(os.path.abspath(__file__))
def get_data_file(rel):
    return os.path.join(root_dir, 'data', rel)


cached_lyrics = {}
lyrics_mutex = threading.Lock()


def get_lyrics(file):
    file = str(file)

    if file not in cached_lyrics:
        physical_file = os.path.join('.', 'config', 'lyrics', file + '.txt')
        if os.path.isfile(physical_file):
            lyrics = ['']
            with open(physical_file) as fp:
                for line in fp:
                    if not line.strip() and lyrics[-1]:
                        lyrics.append('')
                    else:
                        lyrics[-1] += html.escape(line).replace('\n', '<br>')
            with lyrics_mutex:
                cached_lyrics[file] = lyrics
        else:
            return []

    with lyrics_mutex:
        lyric_list = cached_lyrics[file]
    return lyric_list


def get_lyric(file, paragraph):
    return get_lyrics(file)[paragraph]


def clear_lyrics_cache():
    with lyrics_mutex:
        cached_lyrics = {}


@socketio.on('join controller')
def on_join_controller():
    join_room('controller')


@socketio.on('join')
def on_join_controller():
    join_room('client')


@socketio.on('set server lyrics')
def on_set_lyrics(json):
    file = json['file']
    paragraph = json['paragraph']
    text = get_lyric(file, paragraph)
    emit('set client lyrics', text, room='client')


@socketio.on('clear lyrics')
def on_set_lyrics():
    emit('set client lyrics', '', room='client')


@app.route('/list-files')
def list_files():
    return flask.jsonify([html.escape(os.path.splitext(f)[0])
                          for f in os.listdir('./config/lyrics')])


@app.route('/list-styles')
def list_styles():
    return flask.jsonify([html.escape(f)
                          for f in os.listdir('./config/styles')])


@app.route('/get-file', methods=['GET', 'POST'])
def get_file():
    file = request.args.get('file')
    return flask.jsonify(get_lyrics(file))


def ensure_dirs():
    if not os.path.exists('./config/styles'):
        import shutil
        os.makedirs('./config/styles')
        shutil.copy(get_data_file('default.css'), './config/styles/default.css')
        # shutil.copy(get_data_file('bottom.css'), './config/styles/bottom.css')
    if not os.path.exists('./config/lyrics'):
        os.makedirs('./config/lyrics')
    if not os.path.exists('./config/backgrounds'):
        os.makedirs('./config/backgrounds')


@app.route('/styles/<fname>.css')
def stylesheet(fname):
    path = './config/styles/%s.css' % fname
    if os.path.isfile(path):
        return flask.send_file(path)
    return ''


@app.route('/')
def client():
    return flask.send_file(get_data_file('client.html'))


@app.route('/controller')
def controller():
    return flask.send_file(get_data_file('controller.html'))


def main(have_launcher=True):
    def bind_addr_type(value:str):
        if ':' in value:
            res = value.rsplit(':', 1)
        else:
            res = value, 59742
        return res[0], int(res[1])

    import argparse
    parser = argparse.ArgumentParser(description='Renders lyrics on screen')
    parser.add_argument('bind_addr', metavar='HOST:PORT', nargs='?',
        default='127.0.0.1:59742', type=bind_addr_type)
    parser.add_argument('--no-launcher', dest='have_launcher', action='store_false')
    args = parser.parse_args()

    ensure_dirs()
    if args.have_launcher:
        launcher_thread = threading.Thread(target=run_launcher,
                                           kwargs={
                                               'interrupt_main': True,
                                               'clear_lyrics_cache': clear_lyrics_cache,
                                           },
                                           daemon=True)
        launcher_thread.start()
    socketio.run(app, host=args.bind_addr[0], port=args.bind_addr[1])


if __name__ == '__main__':
    main('--no-launcher' not in sys.argv)
