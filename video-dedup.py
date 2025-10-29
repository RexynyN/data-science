import numpy as np
import faiss
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis
import random
import os
import matplotlib.pyplot as plt # Usado apenas para visualização do DTW, não essencial para a lógica central

# --- Configurações Globais ---
# Dimensionalidade dos vetores de características (embeddings)
FEATURE_DIM = 256

# Número de keyframes simulados por vídeo
NUM_KEYFRAMES_PER_VIDEO = 30

# Número total de vídeos na "biblioteca"
NUM_VIDEOS_IN_LIBRARY = 100

# Número de vídeos para simular como "novos" para consulta
NUM_QUERY_VIDEOS = 5

# --- 1. Simulação de Ingestão e Pré-processamento (Extração de Keyframes) ---
def simulate_video_ingestion_and_keyframes(video_id):
    """
    Simula a ingestão de vídeo e a extração de keyframes.
    Na prática, usaria OpenCV/PyAV para ler o vídeo e detecção de cena.
    Retorna uma lista de IDs de keyframes para este vídeo.
    """
    print(f"Simulando ingestão e extração de keyframes para o vídeo: {video_id}")
    # Gerar IDs de keyframes únicos para este vídeo
    keyframes = [f"{video_id}_kf_{i}" for i in range(NUM_KEYFRAMES_PER_VIDEO)]
    return keyframes

# --- 2. Simulação de Extração de Características (Deep Learning) ---
def simulate_feature_extraction(keyframe_id, is_duplicate=False):
    """
    Simula a extração de um vetor de características (embedding) de um keyframe.
    Na prática, usaria um modelo CNN (PyTorch/TensorFlow) para gerar o embedding.
    Se 'is_duplicate' for True, gera um embedding muito similar a um base.
    """
    # Vetor base para simular similaridade
    base_embedding = np.random.rand(FEATURE_DIM).astype('float32') * 100

    if is_duplicate:
        # Cria um embedding muito similar ao base, com um pequeno ruído
        noise = np.random.rand(FEATURE_DIM).astype('float32') * 5
        embedding = base_embedding + noise
    else:
        # Gera um embedding completamente aleatório
        embedding = np.random.rand(FEATURE_DIM).astype('float32') * 100
    
    # Normaliza o embedding (prática comum para busca por similaridade)
    embedding = embedding / np.linalg.norm(embedding)
    return embedding

# --- 3. Indexação e Busca ANN (Faiss) ---
class VideoFeatureIndex:
    def __init__(self, feature_dim):
        """
        Inicializa o índice Faiss.
        Usamos IndexFlatL2 para busca exata (para demonstração),
        mas para escala real, IndexIVFFlat ou HNSW seriam melhores.
        """
        self.feature_dim = feature_dim
        # IndexFlatL2: busca exaustiva de vizinhos mais próximos usando distância L2
        # Para produção, considere faiss.IndexIVFFlat(quantizer, feature_dim, nlist) para ANN
        self.index = faiss.IndexFlatL2(feature_dim)
        self.metadata = [] # Para armazenar (video_id, keyframe_id) correspondente a cada vetor

    def add_features(self, video_id, keyframe_id, feature_vector):
        """
        Adiciona um vetor de características ao índice Faiss.
        """
        # Faiss espera um array 2D, mesmo para um único vetor
        self.index.add(np.array([feature_vector]))
        self.metadata.append((video_id, keyframe_id))

    def search(self, query_feature_vector, k=5):
        """
        Realiza uma busca por vizinhos mais próximos no índice.
        Retorna as distâncias e os índices dos resultados.
        """
        # Faiss espera um array 2D para a consulta
        distances, indices = self.index.search(np.array([query_feature_vector]), k)
        
        results = []
        for i, dist in zip(indices[0], distances[0]):
            if i != -1: # -1 indica que não foi encontrado (pode ocorrer se k > num_features)
                original_video_id, original_keyframe_id = self.metadata[i]
                results.append({
                    'video_id': original_video_id,
                    'keyframe_id': original_keyframe_id,
                    'distance': dist
                })
        return results

# --- 4. Alinhamento Temporal (Dynamic Time Warping - DTW) ---
def compare_video_sequences_dtw(seq1_features, seq2_features):
    """
    Compara duas sequências de vetores de características usando DTW.
    Retorna a distância DTW e o caminho de alinhamento.
    """
    # dtaidistance espera um array numpy 2D (num_pontos, dim_caracteristicas)
    # Certifique-se de que os tipos de dados são float64 para dtaidistance
    s1 = np.array(seq1_features).astype(np.float64)
    s2 = np.array(seq2_features).astype(np.float64)

    # Calcula a distância DTW.
    # 'use_c' para usar a implementação C otimizada (mais rápida)
    # 'keep_internals=True' para obter o caminho de alinhamento
    distance, paths = dtw.warping_paths(s1, s2, use_c=True, keep_internals=True)
    
    # O caminho de alinhamento é o primeiro elemento da tupla paths
    best_path = dtw.best_path(paths)

    return distance, best_path

# --- Função Principal do Pipeline ---
def run_deduplication_pipeline():
    print("--- Iniciando o Pipeline de Detecção de Duplicatas de Vídeo ---")

    # 1. Preparar o índice Faiss
    video_index = VideoFeatureIndex(FEATURE_DIM)

    # Armazenar as sequências de features por vídeo para DTW posterior
    library_video_features = {}

    # 2. Popular a biblioteca com vídeos e suas características
    print("\n--- Processando vídeos da biblioteca ---")
    for i in range(NUM_VIDEOS_IN_LIBRARY):
        video_id = f"lib_video_{i}"
        keyframes = simulate_video_ingestion_and_keyframes(video_id)
        
        video_features_sequence = []
        for kf_id in keyframes:
            # Simula que alguns vídeos da biblioteca são "duplicatas" de um padrão
            is_duplicate_base = (i % 10 == 0) # A cada 10 vídeos, simula uma duplicata base
            feature = simulate_feature_extraction(kf_id, is_duplicate=is_duplicate_base)
            video_index.add_features(video_id, kf_id, feature)
            video_features_sequence.append(feature)
        library_video_features[video_id] = video_features_sequence
    
    print(f"Biblioteca populada com {video_index.index.ntotal} keyframe features.")

    # 3. Processar novos vídeos de consulta e buscar duplicatas
    print("\n--- Processando vídeos de consulta e buscando duplicatas ---")
    query_video_features = {}
    for i in range(NUM_QUERY_VIDEOS):
        query_video_id = f"query_video_{i}"
        
        # Simula um vídeo de consulta que é uma duplicata parcial de um vídeo da biblioteca
        if i == 0: # O primeiro vídeo de consulta será uma duplicata parcial
            print(f"\nSimulando um vídeo de consulta (duplicata parcial): {query_video_id}")
            # Pega um vídeo da biblioteca para ser a base da duplicata parcial
            base_lib_video_id = "lib_video_0"
            base_lib_features = library_video_features[base_lib_video_id]
            
            # Cria uma sequência de features que é um segmento do vídeo base, com ruído
            # Simula uma duplicata parcial com 50% dos keyframes do vídeo base
            segment_len = NUM_KEYFRAMES_PER_VIDEO // 2
            start_idx = random.randint(0, NUM_KEYFRAMES_PER_VIDEO - segment_len)
            
            query_keyframes = [f"{query_video_id}_kf_{j}" for j in range(segment_len)]
            query_features_sequence = []
            for j in range(segment_len):
                # Adiciona ruído ao feature do vídeo base para simular transformações
                noisy_feature = base_lib_features[start_idx + j] + (np.random.rand(FEATURE_DIM).astype('float32') * 0.1)
                noisy_feature = noisy_feature / np.linalg.norm(noisy_feature) # Normaliza
                video_index.add_features(query_video_id, query_keyframes[j], noisy_feature) # Adiciona ao índice para busca
                query_features_sequence.append(noisy_feature)
            query_video_features[query_video_id] = query_features_sequence
            print(f"  - Criado como duplicata parcial de '{base_lib_video_id}'")

        else: # Outros vídeos de consulta são aleatórios
            print(f"\nSimulando um vídeo de consulta (aleatório): {query_video_id}")
            query_keyframes = simulate_video_ingestion_and_keyframes(query_video_id)
            query_features_sequence = []
            for kf_id in query_keyframes:
                feature = simulate_feature_extraction(kf_id)
                video_index.add_features(query_video_id, kf_id, feature)
                query_features_sequence.append(feature)
            query_video_features[query_video_id] = query_features_sequence

        # Para cada keyframe do vídeo de consulta, buscar vizinhos no índice
        print(f"  - Buscando vizinhos próximos para {query_video_id}...")
        all_query_results = []
        for j, q_feature in enumerate(query_features_sequence):
            results = video_index.search(q_feature, k=5)
            # Filtra resultados que não sejam do próprio vídeo de consulta
            filtered_results = [r for r in results if r['video_id'] != query_video_id]
            if filtered_results:
                all_query_results.append({
                    'query_keyframe': f"{query_video_id}_kf_{j}",
                    'matches': filtered_results
                })
        
        if all_query_results:
            print(f"  - Potenciais correspondências encontradas para {query_video_id}:")
            # Agrupar correspondências por vídeo da biblioteca
            potential_duplicates_by_video = {}
            for res in all_query_results:
                for match in res['matches']:
                    lib_video_id = match['video_id']
                    if lib_video_id not in potential_duplicates_by_video:
                        potential_duplicates_by_video[lib_video_id] = []
                    potential_duplicates_by_video[lib_video_id].append({
                        'query_kf': res['query_keyframe'],
                        'lib_kf': match['keyframe_id'],
                        'distance': match['distance']
                    })
            
            for lib_vid_id, matches in potential_duplicates_by_video.items():
                print(f"    -> Com o vídeo da biblioteca '{lib_vid_id}' (correspondências de keyframes: {len(matches)})")
                
                # DTW para confirmar duplicatas parciais
                # Precisamos das sequências completas de features para o DTW
                lib_seq = library_video_features[lib_vid_id]
                query_seq = query_video_features[query_video_id]

                print(f"      - Realizando DTW entre {query_video_id} (len={len(query_seq)}) e {lib_vid_id} (len={len(lib_seq)})")
                dtw_distance, dtw_path = compare_video_sequences_dtw(query_seq, lib_seq)
                print(f"      - Distância DTW: {dtw_distance:.2f}")

                # Um threshold para DTW indicaria uma duplicata parcial
                DTW_THRESHOLD = 0.5 * min(len(query_seq), len(lib_seq)) # Exemplo de threshold
                if dtw_distance < DTW_THRESHOLD:
                    print(f"      -> {query_video_id} É UMA DUPLICATA PARCIAL DE {lib_vid_id}!")
                    # O dtw_path pode ser usado para visualizar o alinhamento
                    # dtwvis.plot_warping(query_seq, lib_seq, dtw_path, filename=f"dtw_plot_{query_video_id}_{lib_vid_id}.png")
                    # print(f"        (Caminho DTW salvo em dtw_plot_{query_video_id}_{lib_vid_id}.png)")
                else:
                    print(f"      -> {query_video_id} NÃO É UMA DUPLICATA PARCIAL SIGNIFICATIVA DE {lib_vid_id}")
        else:
            print(f"  - Nenhuma correspondência significativa encontrada para {query_video_id}.")

    print("\n--- Pipeline Concluído ---")

# Executar o pipeline
if __name__ == "__main__":
    # Garante que o diretório para plots exista (se descomentar a linha do plot)
    # os.makedirs("dtw_plots", exist_ok=True)
    run_deduplication_pipeline()
