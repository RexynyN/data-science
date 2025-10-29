# app.py
import streamlit as st
import pandas as pd
import sqlite3
import os
import shutil
from collections import defaultdict

# cd ~/codes/data-science/compvis/video-sim  &&\
# py indexer_paralell.py "/mnt/c/users/breno_home/documents/pasta"



# --- Configurações ---
DB_PATH = 'video_db.db'
TRASH_FOLDER_NAME = '__trash__'
HAMMING_DISTANCE_THRESHOLD = 10
MIN_SEQUENCE_LENGTH_SEC = 20 # Aumentado para reduzir falsos positivos em cenas de ação curtas

st.set_page_config(layout="wide", page_title="Detector de Vídeos Duplicados")

# --- Funções de Carregamento e Análise (com cache) ---
@st.cache_data(ttl=3600)
def load_data():
    """Carrega dados de hashes e metadados."""
    if not os.path.exists(DB_PATH):
        return None, None
    with sqlite3.connect(DB_PATH) as conn:
        hashes_df = pd.read_sql_query("SELECT video_path, timestamp_sec, p_hash FROM video_hashes", conn)
        metadata_df = pd.read_sql_query("SELECT * FROM video_metadata", conn)
        metadata_df.set_index('video_path', inplace=True)
    return hashes_df, metadata_df

def _hamming_distance(hash1, hash2):
    return bin(int(hash1, 16) ^ int(hash2, 16)).count('1')

def _find_full_duplicates(hashes_df, metadata_df):
    """Encontra duplicatas completas de forma rápida, comparando a assinatura de hashes."""
    video_hashes = hashes_df.groupby('video_path')['p_hash'].apply(tuple)
    hash_signatures = defaultdict(list)
    for video_path, hashes in video_hashes.items():
        hash_signatures[hashes].append(video_path)
    
    full_duplicates = []
    for hashes, paths in hash_signatures.items():
        if len(paths) > 1:
            # Ordena por um critério (ex: bitrate) para sugerir o "original"
            paths.sort(key=lambda p: metadata_df.loc[p]['bitrate_kbps'] if p in metadata_df.index else 0, reverse=True)
            original = paths[0]
            for dup_path in paths[1:]:
                full_duplicates.append({"type": "Completa", "original": original, "duplicate": dup_path})
    return full_duplicates, set(video_hashes.index)

def _find_partial_duplicates(hashes_df, all_video_paths, metadata_df):
    """Encontra duplicatas parciais usando a estratégia de índice invertido (muito mais rápido)."""
    st.write("Construindo índice invertido para análise de duplicatas parciais...")
    
    # Estruturas de dados para acesso rápido
    video_to_hashes = hashes_df.set_index('video_path').groupby('video_path')['p_hash'].apply(list).to_dict()
    inverted_index = defaultdict(list)
    for idx, row in hashes_df.iterrows():
        inverted_index[row['p_hash']].append((row['video_path'], row['timestamp_sec']))

    partial_duplicates = []
    processed_pairs = set()

    # Itera sobre todos os vídeos e seus hashes
    progress_bar = st.progress(0, text="Analisando vídeos em busca de clipes...")
    total_videos = len(all_video_paths)
    
    for i, path_a in enumerate(all_video_paths):
        progress_bar.progress(i / total_videos, text=f"Analisando '{os.path.basename(path_a)}'...")
        
        hashes_a = video_to_hashes.get(path_a, [])
        for time_a, hash_a in enumerate(hashes_a):
            # Encontra todas as outras ocorrências deste hash
            matches = inverted_index.get(hash_a, [])
            if len(matches) > 1:
                for path_b, time_b in matches:
                    if path_a >= path_b: # Evita duplicatas (a,b) e (b,a) e auto-comparação
                        continue

                    # Cria uma chave canônica para o par e o offset de tempo
                    pair_key = (path_a, path_b, time_a, time_b)
                    if pair_key in processed_pairs:
                        continue

                    # Estende a correspondência para ver se é uma sequência longa
                    match_len = 0
                    max_len = min(len(hashes_a) - time_a, len(video_to_hashes.get(path_b, [])) - time_b)
                    for offset in range(max_len):
                        h1 = hashes_a[time_a + offset]
                        h2 = video_to_hashes[path_b][time_b + offset]
                        if _hamming_distance(h1, h2) <= HAMMING_DISTANCE_THRESHOLD:
                            match_len += 1
                        else:
                            break # A sequência foi quebrada

                    if match_len >= MIN_SEQUENCE_LENGTH_SEC:
                        # Evita registrar o mesmo par várias vezes
                        canonical_pair = tuple(sorted((path_a, path_b)))
                        if canonical_pair not in processed_pairs:
                            # Garante que o vídeo mais curto é sempre a "duplicata"
                            dur_a = metadata_df.loc[path_a]['duration_sec']
                            dur_b = metadata_df.loc[path_b]['duration_sec']
                            if dur_a > dur_b:
                                partial_duplicates.append({"type": "Parcial", "original": path_a, "duplicate": path_b})
                            else:
                                partial_duplicates.append({"type": "Parcial", "original": path_b, "duplicate": path_a})
                            processed_pairs.add(canonical_pair)
                        
                        # Marca todos os hashes nesta sequência como processados para este par
                        for offset in range(match_len):
                            processed_pairs.add((path_a, path_b, time_a + offset, time_b + offset))

    progress_bar.empty()
    return partial_duplicates

@st.cache_data(show_spinner=False)
def find_all_duplicates(_hashes_df, _metadata_df):
    """Orquestra a busca por duplicatas completas e parciais."""
    st.write("Procurando por duplicatas completas (cópias exatas)...")
    full_duplicates, all_paths = _find_full_duplicates(_hashes_df, _metadata_df)
    
    st.write(f"Encontradas {len(full_duplicates)} duplicatas completas.")
    
    partial_duplicates = _find_partial_duplicates(_hashes_df, all_paths, _metadata_df)
    
    st.write(f"Encontradas {len(partial_duplicates)} duplicatas parciais potenciais.")
    
    return full_duplicates + partial_duplicates

# --- Funções de UI e Ações (sem alterações, mas repetidas para completude) ---
def move_to_trash(filepath):
    if not os.path.exists(filepath):
        st.error(f"Arquivo não encontrado: {filepath}")
        return False
    try:
        base_dir = os.path.dirname(filepath)
        trash_path = os.path.join(base_dir, TRASH_FOLDER_NAME)
        os.makedirs(trash_path, exist_ok=True)
        shutil.move(filepath, os.path.join(trash_path, os.path.basename(filepath)))
        st.toast(f"Movido '{os.path.basename(filepath)}' para a lixeira.")
        return True
    except Exception as e:
        st.error(f"Erro ao mover arquivo: {e}")
        return False

def display_metadata(path, metadata_df):
    if path not in metadata_df.index:
        st.warning("Metadados não encontrados.")
        return
    meta = metadata_df.loc[path]
    st.markdown(f"**Caminho:** `{path}`")
    cols = st.columns(4)
    cols[0].metric("Tamanho", f"{meta['file_size_mb']:.2f} MB")
    cols[1].metric("Resolução", meta['resolution'])
    cols[2].metric("Bitrate", f"{int(meta['bitrate_kbps'])} kbps")
    cols[3].metric("Score de Nitidez", f"{meta['avg_sharpness']:.2f}")

# --- Lógica Principal da Aplicação ---
st.title("🔎 Detector de Vídeos Duplicados")

hashes_df, metadata_df = load_data()

if hashes_df is None:
    st.warning("Banco de dados `video_index.db` não encontrado. Execute `indexer_parallel.py` primeiro.")
else:
    if 'duplicates' not in st.session_state:
        st.session_state.duplicates = find_all_duplicates(hashes_df, metadata_df)
        st.session_state.current_index = 0

    duplicates = st.session_state.get('duplicates', [])
    idx = st.session_state.get('current_index', 0)
    
    if not duplicates:
        st.success("Nenhuma duplicata encontrada!")
    elif idx >= len(duplicates):
        st.success("🎉 Você validou todas as duplicatas!")
        if st.button("Recarregar e Reanalisar"):
            st.cache_data.clear()
            st.session_state.pop('duplicates', None)
            st.session_state.pop('current_index', None)
            st.rerun()
    else:
        def advance_and_rerun():
            st.session_state.current_index += 1
            st.rerun()

        item = duplicates[idx]
        total = len(duplicates)
        
        st.header(f"Par {idx + 1}/{total} - Tipo: {item['type']}")
        st.progress((idx + 1) / total)

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Vídeo A (Potencial Original/Maior)")
            if os.path.exists(item['original']):
                display_metadata(item['original'], metadata_df)
                st.video(item['original'])
            else:
                st.error("Arquivo de vídeo A não encontrado.")
                advance_and_rerun()

        with col2:
            st.subheader("Vídeo B (Potencial Duplicata/Menor)")
            if os.path.exists(item['duplicate']):
                display_metadata(item['duplicate'], metadata_df)
                st.video(item['duplicate'])
            else:
                st.error("Arquivo de vídeo B não encontrado.")
                advance_and_rerun()


        st.write("---")
        st.subheader("Ações")
        
        action_cols = st.columns(4)
        
        

        if action_cols[0].button("🗑️ Mover Vídeo B", use_container_width=True, type="primary"):
            if move_to_trash(item['duplicate']):
                advance_and_rerun()

        if action_cols[1].button("🗑️ Mover Vídeo A", use_container_width=True):
            if move_to_trash(item['original']):
                advance_and_rerun()
        
        if action_cols[2].button("🗑️ Mover Ambos", use_container_width=True):
            moved_a = move_to_trash(item['original'])
            moved_b = move_to_trash(item['duplicate'])
            if moved_a or moved_b:
                advance_and_rerun()

        if action_cols[3].button("✅ Ignorar (Manter Ambos)", use_container_width=True):
            st.toast("Par ignorado.")
            advance_and_rerun()