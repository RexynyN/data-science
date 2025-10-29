import numpy as np
import faiss
from dtaidistance import dtw
import cv2
import os
import json
import glob
from tqdm import tqdm
import torch
import torchvision.models as models
import torchvision.transforms as transforms

# --- Configurações Globais ---
# Diretório onde os vídeos estão localizados
VIDEO_DIRECTORY = "./videos_para_analise"
# Nome do arquivo de saída JSON
RESULTS_FILE = "resultados_duplicatas.json"
# Dimensionalidade dos vetores de características (embeddings) do MobileNetV2
FEATURE_DIM = 1280 
# Taxa de amostragem de quadros (a cada quantos quadros um é extraído)
FRAME_SAMPLE_RATE = 30
# Limiar para considerar uma mudança de cena (histograma)
SCENE_CHANGE_THRESHOLD = 0.5
# Limiar de distância Faiss para correspondência inicial (ajustar conforme necessário)
FAISS_DISTANCE_THRESHOLD = 0.2
# Limiar de distância DTW para confirmar duplicata parcial (ajustar conforme necessário)
# Isso é uma heurística, o ideal é basear em testes
DTW_DISTANCE_THRESHOLD = 10.0

# --- Funções de Ingestão e Extração de Características ---

def load_model():
    """
    Carrega um modelo pré-treinado (MobileNetV2) e o prepara para extração de características.
    Remove a camada de classificação para obter o vetor de características (embedding).
    """
    try:
        model = models.mobilenet_v2(pretrained=True)
        # Remove a última camada de classificação para obter as features
        model = torch.nn.Sequential(*list(model.children())[:-1])
        model.eval() # Modo de avaliação, sem treinamento
        print("Modelo MobileNetV2 carregado com sucesso.")
        return model
    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")
        return None

def extract_keyframes(video_path):
    """
    Lê um vídeo e extrai keyframes com base na detecção de mudança de cena usando histogramas.
    Retorna uma lista de keyframes como arrays NumPy.
    """
    keyframes = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Erro ao abrir o vídeo: {video_path}")
        return keyframes

    ret, prev_frame = cap.read()
    if not ret:
        return keyframes
    
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_hist = cv2.calcHist([prev_gray], [0], None, [256], [0, 256])
    cv2.normalize(prev_hist, prev_hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    
    frame_count = 0
    keyframes.append(prev_frame) # O primeiro quadro sempre é um keyframe
    
    with tqdm(desc=f"Extraindo keyframes de '{os.path.basename(video_path)}'", unit="frame") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Amostragem para acelerar o processo
            if frame_count % FRAME_SAMPLE_RATE == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
                
                # Compara o histograma do quadro atual com o anterior
                correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                
                # Se a correlação for baixa, é uma mudança de cena
                if correlation < SCENE_CHANGE_THRESHOLD:
                    keyframes.append(frame)
                    prev_hist = hist

            prev_frame = frame
            frame_count += 1
            pbar.update(1)

    cap.release()
    print(f"Extraídos {len(keyframes)} keyframes de '{os.path.basename(video_path)}'.")
    return keyframes

def extract_features(keyframes, model):
    """
    Extrai vetores de características (embeddings) de uma lista de keyframes usando um modelo pré-treinado.
    """
    # Transformações necessárias para o modelo MobileNetV2
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    features = []
    # Usar torch.no_grad() para desabilitar o cálculo de gradientes
    # e otimizar a inferência
    with torch.no_grad():
        for kf in tqdm(keyframes, desc="Extraindo features com DL", unit="keyframe"):
            # Converte o array numpy para tensor e aplica as transformações
            kf_tensor = transform(kf).unsqueeze(0)
            
            # Extrai o embedding do keyframe
            embedding = model(kf_tensor)
            
            # Normaliza o vetor e remove as dimensões desnecessárias
            embedding = embedding.squeeze().numpy()
            embedding = embedding / np.linalg.norm(embedding)
            
            features.append(embedding)

    return np.array(features, dtype='float32')

# --- Funções de Indexação e Busca ---

class VideoFeatureIndex:
    def __init__(self, feature_dim):
        """
        Inicializa o índice Faiss.
        """
        self.feature_dim = feature_dim
        self.index = faiss.IndexFlatL2(feature_dim)
        self.metadata = []

    def add_features(self, video_id, features):
        """
        Adiciona vetores de características de um vídeo ao índice Faiss.
        """
        self.index.add(features)
        # Armazena o ID do vídeo para cada vetor adicionado
        for i in range(len(features)):
            self.metadata.append(video_id)

    def search(self, query_features, k=10):
        """
        Realiza uma busca por vizinhos mais próximos no índice.
        """
        distances, indices = self.index.search(query_features, k)
        
        results = []
        for i in range(len(indices)):
            for j in range(k):
                if indices[i][j] != -1:
                    original_video_id = self.metadata[indices[i][j]]
                    distance = distances[i][j]
                    results.append({
                        'query_feature_idx': i,
                        'original_video_id': original_video_id,
                        'distance': distance
                    })
        return results

# --- Função Principal do Pipeline ---

def run_deduplication_pipeline(video_directory):
    """
    Orquestra o pipeline completo de detecção de duplicatas.
    """
    print("--- Iniciando o Pipeline de Detecção de Duplicatas de Vídeo ---")
    
    # 1. Carregar o modelo de Deep Learning e o índice Faiss
    model = load_model()
    if not model:
        return
    
    video_index = VideoFeatureIndex(FEATURE_DIM)
    
    # Armazenar as sequências de features por vídeo para DTW posterior
    library_video_features = {}
    
    # Encontrar todos os arquivos de vídeo no diretório
    video_files = glob.glob(os.path.join(video_directory, "*.*"))
    print(f"\nEncontrados {len(video_files)} vídeos para processar.")
    
    # 2. Processar todos os vídeos e popular a biblioteca de features
    print("\n--- Etapa 1: Processando vídeos e construindo o índice Faiss ---")
    for video_path in video_files:
        video_id = os.path.basename(video_path)
        try:
            keyframes = extract_keyframes(video_path)
            if not keyframes:
                continue
            
            features = extract_features(keyframes, model)
            
            video_index.add_features(video_id, features)
            library_video_features[video_id] = features
        except Exception as e:
            print(f"Erro ao processar o vídeo '{video_id}': {e}")
    
    print(f"\nBiblioteca populada com {video_index.index.ntotal} keyframe features.")
    
    # 3. Processar cada vídeo como consulta e buscar duplicatas
    print("\n--- Etapa 2: Buscando duplicatas e verificando com DTW ---")
    results = {}
    
    for query_video_id, query_features in tqdm(library_video_features.items(), desc="Analisando vídeos por duplicatas", unit="video"):
        # Buscar vizinhos próximos para cada feature do vídeo de consulta
        all_matches = video_index.search(query_features, k=5)
        
        # Agrupar correspondências por vídeo da biblioteca
        potential_duplicates_by_video = {}
        for match in all_matches:
            lib_video_id = match['original_video_id']
            # Ignora a correspondência com o próprio vídeo
            if lib_video_id == query_video_id:
                continue
                
            if lib_video_id not in potential_duplicates_by_video:
                potential_duplicates_by_video[lib_video_id] = []
            
            potential_duplicates_by_video[lib_video_id].append({
                'query_feature_idx': match['query_feature_idx'],
                'distance': match['distance']
            })

        if potential_duplicates_by_video:
            for lib_vid_id, matches in potential_duplicates_by_video.items():
                # Precisamos das sequências completas de features para o DTW
                lib_seq = library_video_features[lib_vid_id]
                query_seq = library_video_features[query_video_id]

                dtw_distance = dtw.distance(query_seq, lib_seq)
                
                if dtw_distance < DTW_DISTANCE_THRESHOLD:
                    if query_video_id not in results:
                        results[query_video_id] = []
                    results[query_video_id].append({
                        'match_video_id': lib_vid_id,
                        'dtw_distance': dtw_distance,
                        'status': 'Duplicata Parcial Confirmada'
                    })
    
    return results

def save_results_to_json(results, filename):
    """
    Salva o dicionário de resultados em um arquivo JSON.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"\nResultados salvos em '{filename}'.")

# --- Execução Principal ---
if __name__ == "__main__":
    if not os.path.exists(VIDEO_DIRECTORY):
        print(f"Diretório '{VIDEO_DIRECTORY}' não encontrado. Por favor, crie-o e coloque os vídeos lá.")
    else:
        final_results = run_deduplication_pipeline(VIDEO_DIRECTORY)
        if final_results:
            save_results_to_json(final_results, RESULTS_FILE)
        else:
            print("\nNenhuma duplicata significativa encontrada.")
    
    print("\n--- Pipeline de Detecção de Duplicatas Concluído ---")
