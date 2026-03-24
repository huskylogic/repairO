"""
TechMedic - Tool Downloader
Uses Python built-in urllib only (no requests dependency)
This avoids 'No module named email' and similar PyInstaller bundling issues.
"""

import os
import json
import zipfile
import threading
import shutil
import ssl
import urllib.request
import urllib.error
from pathlib import Path


def _make_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class ToolDownloader:
    def __init__(self, base_dir, manifest_path=None, tools_dir=None):
        self.base_dir = base_dir
        self.tools_dir = tools_dir or os.path.join(base_dir, "tools")
        os.makedirs(self.tools_dir, exist_ok=True)

        if manifest_path is None:
            manifest_path = os.path.join(base_dir, "tools_manifest.json")

        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
            self.tools = {t["id"]: t for t in data.get("tools", [])}
        except Exception as e:
            self.tools = {}
            print(f"[Downloader] Failed to load manifest: {e}")

    def is_downloaded(self, tool_id):
        t = self.tools.get(tool_id)
        if not t:
            return False
        exe = os.path.join(self.tools_dir, tool_id, t["filename"])
        return os.path.exists(exe)

    def get_exe_path(self, tool_id):
        t = self.tools.get(tool_id)
        if not t:
            return None
        exe = os.path.join(self.tools_dir, tool_id, t["filename"])
        return exe if os.path.exists(exe) else None

    def download(self, tool_id, progress_cb=None, done_cb=None, error_cb=None):
        t = self.tools.get(tool_id)
        if not t:
            if error_cb:
                error_cb(tool_id, f"Unknown tool: {tool_id}")
            return
        thread = threading.Thread(
            target=self._download_thread,
            args=(t, progress_cb, done_cb, error_cb),
            daemon=True
        )
        thread.start()

    def download_all(self, progress_cb=None, done_cb=None, error_cb=None):
        def worker():
            total = len(self.tools)
            for i, tool_id in enumerate(self.tools):
                if self.is_downloaded(tool_id):
                    if progress_cb:
                        progress_cb(int((i+1)/total*100),
                                    f"[{i+1}/{total}] {self.tools[tool_id]['name']} already downloaded")
                    continue
                done = threading.Event()
                results = {}

                def _prog(pct, msg, _i=i, _total=total):
                    overall = int(_i/_total*100 + pct/_total)
                    if progress_cb:
                        progress_cb(overall, msg)

                def _done(tid):
                    results['ok'] = True
                    done.set()

                def _err(tid, msg):
                    results['err'] = msg
                    done.set()

                self.download(tool_id, _prog, _done, _err)
                done.wait()
                if 'err' in results and error_cb:
                    error_cb(tool_id, results['err'])

            if done_cb:
                done_cb("all")

        threading.Thread(target=worker, daemon=True).start()

    def _download_thread(self, tool, progress_cb, done_cb, error_cb):
        tool_id  = tool["id"]
        name     = tool["name"]
        url      = tool["url"]
        filename = tool["filename"]
        is_zip   = tool.get("is_zip", False)
        zip_file = tool.get("zip_extract_file", "")

        dest_dir = os.path.join(self.tools_dir, tool_id)
        os.makedirs(dest_dir, exist_ok=True)

        if is_zip:
            tmp_zip = os.path.join(dest_dir, f"_tmp_{tool_id}.zip")
            download_target = tmp_zip
        else:
            download_target = os.path.join(dest_dir, filename)

        try:
            if progress_cb:
                progress_cb(5, f"Connecting to download {name}...")

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
            )
            ctx = _make_ssl_context()

            with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 65536

                with open(download_target, "wb") as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_cb:
                            if total_size > 0:
                                pct = int(downloaded / total_size * 85) + 5
                            else:
                                pct = 50
                            mb = downloaded / 1_048_576
                            progress_cb(pct, f"Downloading {name}... {mb:.1f} MB")

            if is_zip:
                if progress_cb:
                    progress_cb(90, f"Extracting {name}...")
                try:
                    with zipfile.ZipFile(tmp_zip, 'r') as zf:
                        if zip_file:
                            matched = [n for n in zf.namelist()
                                       if os.path.basename(n).lower() == zip_file.lower()]
                            if matched:
                                data = zf.read(matched[0])
                                out_path = os.path.join(dest_dir, filename)
                                with open(out_path, 'wb') as f:
                                    f.write(data)
                            else:
                                zf.extractall(dest_dir)
                        else:
                            zf.extractall(dest_dir)
                finally:
                    try:
                        os.remove(tmp_zip)
                    except:
                        pass

            final_exe = os.path.join(dest_dir, filename)
            if not os.path.exists(final_exe):
                exes = list(Path(dest_dir).glob("*.exe"))
                if exes:
                    shutil.copy2(str(exes[0]), final_exe)
                else:
                    raise FileNotFoundError(
                        f"Download finished but {filename} not found.\n"
                        f"Files in folder: {os.listdir(dest_dir)}"
                    )

            if progress_cb:
                progress_cb(100, f"✅ {name} ready!")
            if done_cb:
                done_cb(tool_id)

        except urllib.error.HTTPError as e:
            msg = f"HTTP {e.code}: {e.reason}\nThe download URL may have changed."
            if error_cb: error_cb(tool_id, msg)
        except urllib.error.URLError as e:
            msg = f"Network error: {e.reason}\nCheck your internet connection."
            if error_cb: error_cb(tool_id, msg)
        except Exception as e:
            if error_cb: error_cb(tool_id, f"{type(e).__name__}: {e}")
        finally:
            if is_zip and os.path.exists(download_target):
                try: os.remove(download_target)
                except: pass

    def launch(self, tool_id):
        import subprocess
        t = self.tools.get(tool_id)
        if not t:
            return False, f"Unknown tool: {tool_id}"
        exe = self.get_exe_path(tool_id)
        if not exe:
            return False, f"{t['name']} is not downloaded yet."
        try:
            args = t.get("launch_args", [])
            subprocess.Popen([exe] + args)
            return True, ""
        except Exception as e:
            return False, str(e)
