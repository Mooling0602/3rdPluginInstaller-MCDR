import threading


stop_event = threading.Event()
download_lock = threading.Lock()