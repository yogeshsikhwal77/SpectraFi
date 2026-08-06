import os 
import shutil


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR,"data")
TEMP_UPLOADS_DIR = os.path.join(DATA_DIR, "temp_uploads")
TEMP_IMAGES_DIR = os.path.join(DATA_DIR, "temp_images")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")

def ensure_dir():
    """ ensure all directries are avaible """
    os.makedirs(TEMP_UPLOADS_DIR,exist_ok=True)
    os.makedirs(CHROMA_DB_DIR,exist_ok=True)
    os.makedirs(TEMP_IMAGES_DIR,exist_ok=True)


def save_file(file):

    """save all files come via streamlit"""

    ensure_dir()

    file_path = os.path.join(TEMP_UPLOADS_DIR,file.name)

    with open(file_path,"wb") as f:
        f.write(file.getbuffer())

    print(f"file handler saved to {file_path}")
   
    return file.name

def clear_file():
    """ delete temproary files """
    for directory in [TEMP_IMAGES_DIR,TEMP_UPLOADS_DIR]:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory,filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)

                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"failed to delete {file_path}. Reason : {e}")