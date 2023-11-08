def assert_path(path) -> bool:
    is_path = os.path.isdir(path)
    if not is_path:
        os.mkdir(path)
    
    return is_path

def split_train_data():
    for iclass in os.listdir(TRAIN_PATH):
        test_path = path_join(TEST_PATH, iclass)
        train_path = path_join(path_join(TRAIN_PATH, iclass))
        assert_path(test_path)

        images = os.listdir(train_path)
        class_images = [f for f in images if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        random.shuffle(class_images)
        split_idx = floor(len(images) * TEST_SPLIT) 
        

        test_images = class_images[:split_idx] 
        for img in test_images:
            os.rename(path_join(train_path, img), path_join(test_path, img))


def undo_train_split():
    for iclass in os.listdir(TRAIN_PATH):
        test_path = path_join(TEST_PATH, iclass)
        train_path = path_join(path_join(TRAIN_PATH, iclass))
        assert_path(test_path)

        for img in os.listdir(test_path):
            os.rename(path_join(test_path, img), path_join(train_path, img))