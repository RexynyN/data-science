# indexer_parallel.py
import cv2
import sqlite3
import os
import imagehash
from PIL import Image
import argparse
from tqdm import tqdm
import concurrent.futures
import time
import subprocess
import json
import numpy as np
import shutil

# py indexer_paralell.py "/mnt/d/Back-Up/Downloads/folder/porterting" &&\
# py indexer_paralell.py "/mnt/d/Back-Up/Downloads/folder/porterting/chunked"


# py indexer_paralell.py "/mnt/f/Mídia/Inspiração/Personalidades/nem-tão-insp-assim/gimp"


os.environ['OPENCV_FFMPEG_LOGLEVEL'] = "-8"

# --- Configurações ---
DB_PATH = 'video_db.db'
FRAMES_PER_SECOND_TO_SAMPLE = 1
MAX_WORKERS = None
SHARPNESS_SAMPLE_COUNT = 10 # Nº de quadros a serem amostrados para o cálculo de nitidez

def get_video_metadata(video_path):
    """Usa ffprobe para extrair metadados essenciais do vídeo."""
    try:
        command = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,bit_rate,duration',
            '-of', 'json',
            video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)['streams'][0]
        
        # Bitrate pode ser N/A, então fornecemos um padrão
        bitrate = int(data.get('bit_rate', '0')) // 1000 # em kbps
        duration = float(data.get('duration', '0'))
        resolution = f"{data.get('width', 0)}x{data.get('height', 0)}"
        
        return resolution, bitrate, duration
    except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError, KeyError) as e:
        # print(f"Aviso: Não foi possível obter metadados ffprobe para {video_path}: {e}")
        return "0x0", 0, 0

def calculate_sharpness(cap, frame_count, fps):
    """Calcula um score médio de nitidez amostrando quadros do vídeo."""
    if frame_count < SHARPNESS_SAMPLE_COUNT:
        return 0.0

    sharpness_scores = []
    sample_points = np.linspace(0, frame_count - 1, SHARPNESS_SAMPLE_COUNT, dtype=int)

    for frame_pos in sample_points:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Calcula a variância do Laplaciano
            lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_scores.append(lap_var)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Reseta o ponteiro do vídeo
    return np.mean(sharpness_scores) if sharpness_scores else 0.0

def create_database():
    """Cria as tabelas no banco de dados se não existirem."""
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        cursor = conn.cursor()
        # Tabela de Hashes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_path TEXT NOT NULL,
                timestamp_sec INTEGER NOT NULL,
                p_hash TEXT NOT NULL,
                UNIQUE(video_path, timestamp_sec)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vpath_time ON video_hashes (video_path, timestamp_sec);')

        # Nova Tabela de Metadados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_metadata (
                video_path TEXT PRIMARY KEY,
                duration_sec REAL,
                resolution TEXT,
                file_size_mb REAL,
                bitrate_kbps INTEGER,
                avg_sharpness REAL
            )
        ''')
        conn.commit()

def get_processed_videos():
    """Retorna um conjunto de vídeos que já têm metadados e hashes."""
    if not os.path.exists(DB_PATH):
        return set()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            # Consideramos um vídeo processado se ele estiver na tabela de metadados
            cursor.execute('SELECT DISTINCT video_path FROM video_metadata')
            return {row[0] for row in cursor.fetchall()}
        except sqlite3.OperationalError:
            return set()
        
def process_video_worker(video_path):
    """Função de trabalho para um único processo."""
    temp_video_path = None
    try:
        # --- 0. Se necessário, copia o vídeo para ./temp ---
        if not video_path.startswith("/mnt/c/"):
            os.makedirs("temp", exist_ok=True)
            temp_video_path = os.path.join("temp", os.path.basename(video_path))
            shutil.copy2(video_path, temp_video_path)
            video_to_process = temp_video_path
        else:
            video_to_process = video_path

        # --- 1. Extração de Metadados ---
        resolution, bitrate, duration = get_video_metadata(video_to_process)
        if duration == 0:
             return (video_path, "Erro: Duração do vídeo é zero ou inválida.")
        
        file_size_mb = round(os.path.getsize(video_path) / (1024 * 1024), 2)
        
        cap = cv2.VideoCapture(video_to_process)
        if not cap.isOpened():
            return (video_path, "Erro: Não foi possível abrir com OpenCV.")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        avg_sharpness = calculate_sharpness(cap, total_frames, fps)

        # --- 2. Extração de Hashes ---
        hashes_to_insert = []
        frame_interval = int(fps / FRAMES_PER_SECOND_TO_SAMPLE) if fps > 0 else 1
        if frame_interval == 0: frame_interval = 1
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret: break

            if frame_count % frame_interval == 0:
                timestamp_sec = int(frame_count / fps)
                pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                p_hash = str(imagehash.phash(pil_img))
                hashes_to_insert.append((video_path, timestamp_sec, p_hash))  # salva o caminho original
            frame_count += 1
        cap.release()

        # --- 3. Inserção no Banco de Dados ---
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Insere metadados (substitui se já existir)
            cursor.execute(
                'INSERT OR REPLACE INTO video_metadata VALUES (?, ?, ?, ?, ?, ?)',
                (video_path, duration, resolution, file_size_mb, bitrate, avg_sharpness)
            )
            # Insere hashes
            if hashes_to_insert:
                cursor.executemany(
                    'INSERT OR IGNORE INTO video_hashes (video_path, timestamp_sec, p_hash) VALUES (?, ?, ?)',
                    hashes_to_insert
                )
            conn.commit()
        
        return (video_path, "Sucesso")

    except Exception as e:
        return (video_path, f"Erro inesperado: {e}")
    finally:
        # Remove o arquivo temporário, se criado
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
            except Exception:
                pass

def main(video_folder):
    start_time = time.time()
    create_database()
    
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    video_files = [os.path.join(root, file) 
                   for root, _, files in os.walk(video_folder) 
                   for file in files if file.lower().endswith(video_extensions)]
    
    processed_videos = get_processed_videos()
    videos_to_process = sorted([f for f in video_files if f not in processed_videos])

    if not videos_to_process:
        print("Nenhum vídeo novo para indexar. O banco de dados está atualizado.")
        return

    print(f"Encontrados {len(videos_to_process)} novos vídeos para indexar...")
    print(f"Iniciando pool com até {MAX_WORKERS or os.cpu_count()} processos trabalhadores.")

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_video = {executor.submit(process_video_worker, path): path for path in videos_to_process}
        
        for future in tqdm(concurrent.futures.as_completed(future_to_video), total=len(videos_to_process), desc="Indexando Vídeos"):
            path, result = future.result()
            if "Erro" in result:
                tqdm.write(f"Falha ao processar {os.path.basename(path)}: {result}")
    
    end_time = time.time()
    print("\nIndexação concluída!")
    print(f"Tempo total: {time.strftime('%H:%M:%S', time.gmtime(end_time - start_time))}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Indexa vídeos e seus metadados de forma paralela.")
    parser.add_argument("folder", type=str, help="O caminho para a pasta contendo os vídeos.")
    args = parser.parse_args()
    
    if not os.path.isdir(args.folder):
        print(f"Erro: O caminho '{args.folder}' não é um diretório válido.")
    else:
        main(args.folder)