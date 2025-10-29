# indexer.py
import cv2
import sqlite3
import os
import imagehash
from PIL import Image
import argparse
from tqdm import tqdm
import shutil

# --- Configurações ---
DB_PATH = 'video_index.db'
FRAMES_PER_SECOND_TO_SAMPLE = 1  # Extrai 1 quadro por segundo. Aumente para mais precisão, diminua para mais velocidade.
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")



os.makedirs(TEMP_DIR, exist_ok=True)

def create_database():
    """Cria a tabela no banco de dados se ela não existir."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_path TEXT NOT NULL,
                timestamp_sec INTEGER NOT NULL,
                p_hash TEXT NOT NULL,
                UNIQUE(video_path, timestamp_sec)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_path ON video_hashes (video_path);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_p_hash ON video_hashes (p_hash);')
        conn.commit()

def get_processed_videos():
    """Retorna um conjunto de caminhos de vídeos que já estão no banco de dados."""
    if not os.path.exists(DB_PATH):
        return set()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT video_path FROM video_hashes')
        return {row[0] for row in cursor.fetchall()}

def process_video(video_path, conn):
    """Extrai quadros, calcula hashes e os insere no banco de dados."""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Erro: Não foi possível abrir o vídeo {video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            print(f"Aviso: FPS do vídeo {video_path} é zero. Pulando.")
            return

        frame_interval = int(fps / FRAMES_PER_SECOND_TO_SAMPLE)
        if frame_interval == 0:
            frame_interval = 1

        hashes_to_insert = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                timestamp_sec = int(frame_count / fps)
                
                # Converte o quadro (array numpy BGR) para uma imagem PIL (RGB)
                pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # Calcula o hash perceptual
                p_hash = str(imagehash.phash(pil_img))
                
                hashes_to_insert.append((video_path, timestamp_sec, p_hash))

            frame_count += 1

        cap.release()

        # Insere todos os hashes de uma vez para eficiência
        if hashes_to_insert:
            cursor = conn.cursor()
            cursor.executemany(
                'INSERT OR IGNORE INTO video_hashes (video_path, timestamp_sec, p_hash) VALUES (?, ?, ?)',
                hashes_to_insert
            )
            conn.commit()
            
    except Exception as e:
        print(f"Erro inesperado ao processar {video_path}: {e}")



def main(video_folder):
    """Função principal para encontrar e processar todos os vídeos."""
    create_database()
    
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    video_files = [os.path.join(root, file) 
                   for root, _, files in os.walk(video_folder) 
                   for file in files if file.lower().endswith(video_extensions)]
    
    processed_videos = get_processed_videos()
    videos_to_process = [f for f in video_files if f not in processed_videos]

    if not videos_to_process:
        print("Nenhum vídeo novo para indexar. O banco de dados está atualizado.")
        return

    print(f"Encontrados {len(videos_to_process)} novos vídeos para indexar...")

    with sqlite3.connect(DB_PATH) as conn:
        # Usando tqdm para uma barra de progresso
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp"), exist_ok=True)
        with tqdm(total=len(videos_to_process), desc="Indexando Vídeos") as pbar:
            for video_path in videos_to_process:
                # Se o vídeo não está em /mnt/c/, faz uma cópia temporária
                if not video_path.startswith("/mnt/c/"):
                    temp_path = os.path.join(TEMP_DIR, os.path.basename(video_path))
                    try:
                        shutil.copy2(video_path, temp_path)
                        process_video(temp_path, conn)
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                else:
                    process_video(video_path, conn)
                pbar.update(1)


        # with tqdm(total=len(videos_to_process), desc="Indexando Vídeos") as pbar:
        #     for video_path in videos_to_process:
        #         process_video(video_path, conn)
        #         pbar.update(1)

    print("Indexação concluída!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Indexa vídeos em uma pasta para detecção de duplicatas.")
    parser.add_argument("folder", type=str, help="O caminho para a pasta contendo os vídeos.")
    args = parser.parse_args()
    
    if not os.path.isdir(args.folder):
        print(f"Erro: O caminho '{args.folder}' não é um diretório válido.")
    else:
        main(args.folder)