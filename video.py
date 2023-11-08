import gc
import os
import sys
import json
import cv2
import imagehash
from os.path import join as join_path
from PIL import Image
from imagehash import ImageHash


class VideoFile():
    def __init__(self, filename: str, frame_timer: float = 5, frame_format: tuple = ()) -> None:
        self.filename = filename
        self.frame_timer = frame_timer
        self.blob = filename.split(os.path.sep)[-1].split(".")[0]
        self.duration = self._get_duration()
        if self.duration <= self.frame_timer:
            self.frame_timer = 1

        self.size = self._get_size()
        self.frame_hashes = self._get_formatted_frames()

    def get_frames(self):
        return self.timed_frames
    
    def _get_duration(self):
        video = cv2.VideoCapture(self.filename)
        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = video.get(cv2.CAP_PROP_FPS)
        return float(frame_count/fps)

    def _get_size(self):
        try:
            file_size = os.path.getsize(self.filename)
            return file_size
        except FileNotFoundError:
            print("File not found.")

    def _get_formatted_frames(self):
        # https://aws.amazon.com/pt/blogs/media/metfc-automatically-compare-two-videos-to-find-common-content/
        vidcap = cv2.VideoCapture(self.filename)
        # success, frame = vidcap.read()
        success = True
        count, frame_hashes, timer  = 0, [], self.frame_timer * 1000
        while True:
            # Extracts a frame every "timer" seconds
            vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * timer)) 
            success, frame = vidcap.read()
            if not success:
                break 
            # Converting to PIL image
            color_converted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(color_converted)
            count += 1

            crop_x1, crop_x2 = 0, image.width
            crop_y1, crop_y2 = int(image.height * 0.333), int(image.height * 0.666)
            # Crops fractions of the image's height to diminish the processing time
            cropped_frame = image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
            frame_hashes.append(imagehash.phash(cropped_frame))

        return frame_hashes
        
    def __eq__(self, other: object) -> bool:
        if isinstance(other, VideoFile):
            return self.size == other.size and self.duration == other.duration
        return False 
    
    # Default values are the one expressed in the amazon's article
    def compare_frame_window(self, compare_hashes: list[ImageHash], max_diff: float = 0.25, MATCH_MIN: float = 0.7):
        if max_diff > 1 or max_diff < 0:
            raise ValueError("Max Diff must be 0 <= diff <= 1")
        else:
            # 64 bits are compared, so we get "max_diff" percent of the total
            MAX_DIFF = 64 * max_diff

        num_matches = 0
        for hash1 in self.frame_hashes:
            for hash2 in compare_hashes:
                # Subtracting hashes returns the # bits difference
                hash_diff = hash1 - hash2
                if hash_diff <= MAX_DIFF:
                    num_matches += 1
                    compare_hashes.remove(hash2)  # only count each matching item once
                    break  # skip the rest since we've found a match

        # how many of hashes_1 were found in hashes_2, and vice versa?
        num_compared = len(self.frame_hashes) 
        if num_compared == 0:
            num_compared = 1
        matched = (num_matches / num_compared) >= MATCH_MIN
        return matched

def main(args):
    PATH = r"/mnt/c/Users/Admin/Downloads/crocs/ploc"

    videos: list[VideoFile] = []
    for file in [x for x in os.listdir(PATH) if x.endswith(".mp4")]:
        print(f"Serializing {file.split(os.path.sep)[-1]}...")
        new_video = VideoFile(join_path(PATH, file))
        videos.append(new_video)
        # Explicitly run the garbage collector to get rid of the frames list
        gc.collect()
    

    # Triangular comparing (triangular matrix-like)
    matches = []
    for index, video in enumerate(videos):
        print(f"Comparing current video => {video.filename}")
        for comp in videos[index + 1:]:
            if video.compare_frame_window(comp.frame_hashes):
                matches.append({"link": video.filename, "dup": comp.filename}) 

    with open("duplicates.json", "w", encoding="utf-8") as f:
        json.dump(matches, f)

if __name__ == "__main__":
    main(sys.argv[1:])
