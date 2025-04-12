from flask import Flask, jsonify, render_template, send_file
from flask_cors import CORS
import random
import os
from PIL import Image
from io import BytesIO
import sqlite3
from functools import wraps
import requests  # Importação do módulo requests

app = Flask(__name__,
            template_folder='../frontend',
            static_folder='../frontend/src')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/location', methods=['GET'])
def get_location():
    return jsonify({
        "name": "Igreja Presbiteriana em Palmeiras-BA",
        "address": "Rua Coronel Dreger, ao lado esquerdo da travessa do fórum - Palmeiras, Bahia, Brasil",
        "coordinates": {
            "latitude": -12.5152504,
            "longitude": -41.5760951
        }
    })

@app.route('/api/photos', methods=['GET'])
def get_photos():
    photos_path = os.path.join('frontend', 'src', 'imgs', 'igr')
    photos = []
    if os.path.exists(photos_path):
        for file in os.listdir(photos_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                photos.append({
                    'url': f'/src/imgs/igr/{file}',
                    'description': file.split('.')[0].replace('_', ' ')
                })
    return jsonify(photos)

def init_db():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, count INTEGER)''')
    c.execute('INSERT OR IGNORE INTO visitors (id, count) VALUES (1, 0)')
    conn.commit()
    conn.close()

def get_visitor_count():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute('SELECT count FROM visitors WHERE id = 1')
    count = c.fetchone()[0]
    conn.close()
    return count

def increment_visitor_count():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute('UPDATE visitors SET count = count + 1 WHERE id = 1')
    conn.commit()
    conn.close()

def track_visitors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if f.__name__ == 'index':
            increment_visitor_count()  # Incrementa a contagem de visitantes
        return f(*args, **kwargs)
    return decorated_function

@app.route('/visitor-count')
def visitor_count():
    return jsonify({'count': get_visitor_count()})

def optimize_image(image_path, max_size=800):
    img = Image.open(image_path)
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    output = BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    return output

@app.route('/optimized-image/<path:image_path>')
def serve_optimized_image(image_path):
    full_path = os.path.join('frontend', 'src', 'imgs', image_path)
    if os.path.exists(full_path):
        return send_file(
            optimize_image(full_path),
            mimetype='image/jpeg'
        )
    return '', 404

@app.route('/random_verse', methods=['GET'])
def get_random_verse():
    try:
        response = requests.get('https://bible-api.com/random')
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx ou 5xx
        data = response.json()
        return jsonify({
            "reference": f"{data['reference']}",
            "text": data['text']
        })
    except requests.exceptions.RequestException as e:
        # Fallback para versículos locais em caso de erro
        verses = [
            {"reference": "João 3:16", "text": "Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna."},
            {"reference": "Salmos 23:1", "text": "O Senhor é o meu pastor, nada me faltará."},
            {"reference": "Filipenses 4:13", "text": "Posso todas as coisas em Cristo que me fortalece."},
            {"reference": "Isaías 41:10", "text": "Não temas, porque eu sou contigo; não te assombres, porque eu sou teu Deus; eu te fortaleço, e te ajudo, e te sustento com a destra da minha justiça."},
            {"reference": "Romanos 8:28", "text": "E sabemos que todas as coisas contribuem juntamente para o bem daqueles que amam a Deus, daqueles que são chamados segundo o seu propósito."}
        ]
        return jsonify(random.choice(verses))

@app.route('/api/verse/<book>/<chapter>', methods=['GET'])
def get_bible_chapter(book, chapter):
    try:
        response = requests.get(f'https://bible-api.com/{book}+{chapter}?translation=almeida')
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'reference': data.get('reference', ''),
                'text': data.get('text', '').replace('\n', ' ')
            })
        else:
            return jsonify({'error': 'Capítulo não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar', methods=['GET'])
def get_calendar():
    return jsonify({
        "calendar_url": "https://calendar.google.com/calendar/embed?src=pt.brazilian%23holiday%40group.v.calendar.google.com&ctz=America%2FSao_Paulo&mode=MONTH&showTitle=0&showNav=1&showDate=1&showPrint=0&showTabs=0&showCalendars=0&showTz=0"
    })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    docs_path = os.path.join('frontend', 'src', 'docs')
    documents = []
    if os.path.exists(docs_path):
        for file in os.listdir(docs_path):
            if file.lower().endswith(('.pdf', '.docx')):
                documents.append({
                    'name': file,
                    'path': f'/src/docs/{file}'
                })
    return jsonify(documents)

@app.route('/api/music', methods=['GET'])
def get_music():
    try:
        # Lista de músicas da playlist
        playlist = [
            {"title": "Teu Povo", "videoId": "4GC0uxYbJ-M"},
            {"title": "Porque Ele Vive", "videoId": "mgUasyYzCKQ"},
            {"title": "Castelo Forte", "videoId": "RGCzQjFKk2w"},
            {"title": "Isaías 53 & Foi na Cruz", "videoId": "HML9NUQJZEU"},
            {"title": "Maravilhosa Graça", "videoId": "c7hw86kSAvw"},
            {"title": "Firmeza na Fé", "videoId": "w_T_fG30TFw"},
            {"title": "Ao Pé da Cruz", "videoId": "2C6EPo0GE3I"},
            {"title": "O Rei Está Aqui", "videoId": "1oh4hdg0IAg"},
            {"title": "Noite de Paz", "videoId": "hjF4jI8jNAY"},
            {"title": "A Rua e o Mundo", "videoId": "3E84QBUyZFo"},
            {"title": "Êxodo", "videoId": "xgE_rNyOoSI"},
            {"title": "Oh Quão Lindo esse Nome É", "videoId": "uV6rRUc35io"},
            {"title": "Encarnação", "videoId": "rQctRkKODN8"},
            {"title": "Trindade Santíssima", "videoId": "z3nPTt2NiUo"},
            {"title": "É o Teu Povo", "videoId": "7DH_tKN_n-g"},
            {"title": "Recebe a Honra", "videoId": "NRcVLMbdD58"}
        ]
        return jsonify(playlist)
    except Exception as e:
        print(f"Error fetching music: {e}")

    # Fallback em caso de erro
    return jsonify([{
        "title": "Erro ao carregar músicas",
        "artist": "Tente novamente mais tarde",
        "cover": "/src/imgs/acs/logo_ipp.png",
        "audio": ""
    }])

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print("Trying alternate port...")
            app.run(host='0.0.0.0', port=5001, debug=True)