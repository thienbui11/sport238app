"""Dùng chung cho pytest: bật máy chủ quản trị Node với dữ liệu mẫu trong thư mục tạm (không đụng dữ liệu thật)."""
import json, os, pathlib, shutil, socket, subprocess, sys, time, urllib.request

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP = ROOT / "sport-shop-app"
sys.path.insert(0, str(APP / "tools"))
PASSWORD = "mat-khau-kiem-thu"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture()
def server(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    shutil.copy(APP / "data" / "seed-products.json", data / "seed-products.json")
    port = free_port()
    env = dict(os.environ, DATA_DIR=str(data), PORT=str(port), ADMIN_PASSWORD=PASSWORD)
    p = subprocess.Popen(["node", "--disable-warning=ExperimentalWarning", "src/server.js"], cwd=APP, env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            urllib.request.urlopen(url + "/api/config", timeout=1)
            break
        except OSError:
            time.sleep(0.1)
    yield {"url": url, "data": data, "password": PASSWORD}
    p.terminate()
    p.wait(10)


def admin_get(server, path):
    req = urllib.request.Request(server["url"] + "/api/admin/login", data=json.dumps({"password": server["password"]}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        cookie = r.headers["Set-Cookie"].split(";")[0]
    with urllib.request.urlopen(urllib.request.Request(server["url"] + path, headers={"Cookie": cookie})) as r:
        return json.load(r)


def admin_post(server, path, obj):
    req = urllib.request.Request(server["url"] + "/api/admin/login", data=json.dumps({"password": server["password"]}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        cookie = r.headers["Set-Cookie"].split(";")[0]
    req = urllib.request.Request(server["url"] + path, data=json.dumps(obj).encode(), headers={"Content-Type": "application/json", "Cookie": cookie})
    with urllib.request.urlopen(req) as r:
        return json.load(r)
