"""
素材文件夹监控模块
使用 watchdog 实时监控指定文件夹的视频文件变化，并自动导入到数据库
"""

import os
import sqlite3
import time
import uuid
from pathlib import Path
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from conf import BASE_DIR, SUPPORTED_VIDEO_EXTENSIONS

class MaterialFileHandler(FileSystemEventHandler):
    """素材文件事件处理器"""

    def __init__(self, video_dir):
        super().__init__()
        self.video_dir = Path(video_dir)
        self.processed_files = set()  # 已处理的文件集合，避免重复处理

    def on_created(self, event):
        """当文件被创建时触发"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # 检查是否是支持的视频文件
        if file_path.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
            return

        # 避免重复处理
        if str(file_path) in self.processed_files:
            return

        # 等待文件完全写入（避免文件正在复制时就开始处理）
        time.sleep(1)

        # 检查文件是否完全写入（文件大小不再变化）
        if not self._wait_for_file_stable(file_path):
            print(f"[WARN] 文件 {file_path.name} 可能未完全复制，跳过")
            return

        print(f"[INFO] 检测到新视频文件: {file_path.name}")
        self.import_to_database(file_path)
        self.processed_files.add(str(file_path))

    def _wait_for_file_stable(self, file_path, max_wait=10):
        """等待文件大小稳定，确保文件已完全写入"""
        try:
            last_size = -1
            wait_time = 0
            while wait_time < max_wait:
                current_size = file_path.stat().st_size
                if current_size == last_size and current_size > 0:
                    return True
                last_size = current_size
                time.sleep(0.5)
                wait_time += 0.5
            return False
        except Exception as e:
            print(f"[ERROR] 检查文件稳定性失败: {e}")
            return False

    def import_to_database(self, file_path):
        """将文件导入到数据库"""
        try:
            # 生成 UUID 和新文件名
            uuid_v1 = uuid.uuid1()
            new_filename = f"{uuid_v1}_{file_path.name}"
            new_file_path = self.video_dir / new_filename

            # 如果文件不在 videoFile 目录，则复制过去
            if file_path.parent != self.video_dir:
                import shutil
                shutil.copy2(file_path, new_file_path)
                print(f"[INFO] 文件已复制到: {new_file_path}")
            else:
                new_file_path = file_path
                new_filename = file_path.name

            # 计算文件大小 (MB)
            filesize = round(new_file_path.stat().st_size / (1024 * 1024), 2)

            # 插入数据库
            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO file_records (filename, filesize, file_path)
                    VALUES (?, ?, ?)
                ''', (file_path.name, filesize, new_filename))
                conn.commit()
                print(f"[OK] 素材已导入数据库: {file_path.name} ({filesize} MB)")

        except Exception as e:
            print(f"[ERROR] 导入素材失败: {e}")


class FolderWatcher:
    """文件夹监控器"""

    def __init__(self):
        self.observer = None
        self.watch_path = None
        self.is_running = False
        self.video_dir = Path(BASE_DIR / "videoFile")

    def start_watching(self, folder_path):
        """开始监控指定文件夹"""
        if self.is_running:
            print("[WARN] 监控已在运行中")
            return False

        if not os.path.exists(folder_path):
            print(f"[ERROR] 文件夹不存在: {folder_path}")
            return False

        try:
            self.watch_path = folder_path
            event_handler = MaterialFileHandler(self.video_dir)
            self.observer = Observer()
            self.observer.schedule(event_handler, folder_path, recursive=False)
            self.observer.start()
            self.is_running = True
            print(f"[OK] 开始监控文件夹: {folder_path}")

            # 首次启动时扫描现有文件
            self._scan_existing_files(folder_path, event_handler)

            return True
        except Exception as e:
            print(f"[ERROR] 启动监控失败: {e}")
            return False

    def _scan_existing_files(self, folder_path, handler):
        """扫描现有文件并导入"""
        try:
            folder = Path(folder_path)
            for file_path in folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS:
                    # 检查文件是否已在数据库中
                    if not self._file_exists_in_db(file_path.name):
                        print(f"[INFO] 发现现有文件: {file_path.name}")
                        handler.import_to_database(file_path)
                        handler.processed_files.add(str(file_path))
        except Exception as e:
            print(f"[ERROR] 扫描现有文件失败: {e}")

    def _file_exists_in_db(self, filename):
        """检查文件是否已在数据库中"""
        try:
            with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM file_records WHERE filename = ?', (filename,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"[ERROR] 查询数据库失败: {e}")
            return False

    def stop_watching(self):
        """停止监控"""
        if not self.is_running:
            print("[WARN] 监控未运行")
            return False

        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
            self.is_running = False
            print("[OK] 已停止监控")
            return True
        except Exception as e:
            print(f"[ERROR] 停止监控失败: {e}")
            return False

    def get_status(self):
        """获取监控状态"""
        return {
            'is_running': self.is_running,
            'watch_path': self.watch_path
        }


# 全局文件夹监控实例
folder_watcher = FolderWatcher()
