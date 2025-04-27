import os
import os.path as op

import re
from pathlib import Path
from time import time


def log(*args):
    print(*args)


class Utils:

    @staticmethod
    def filter_files(src_dir, filter=None):
        files = []
        filter = filter or {}
        include = filter.get('include')
        if include:
            files.extend([
                file_name for file_name in os.listdir(src_dir)
                if re.search(include, file_name)
            ])
        else:
            files = os.listdir(src_dir)
        files = sorted(files)
        sz = len(files)

        ret = []
        skip = filter.get('skip', 0)
        count = filter.get('count', sz)
        for i in range(skip, sz):
            if count <= 0:
                break
            ret.append(files[i])
            count -= 1

        return ret

    @staticmethod
    def write_file(out_path, context):
        if not out_path:
            return
        assert context is not None, f"write_file内容不能空"

        out_dir = op.dirname(out_path)
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(context)
            log(f"  写文件> {out_path} 长:{len(context)}")

    @staticmethod
    def thread(process, tasks, max=8, **kw):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        ti = time()
        with ThreadPoolExecutor(max_workers=max) as exec:
            futures = [exec.submit(process, t, **kw) for t in tasks]
            results = [f.result() for f in as_completed(futures)]
        cost = time() - ti
        return results.count(True), cost

    @staticmethod
    def thread_kw(process, tasks, max=8):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        ti = time()
        with ThreadPoolExecutor(max_workers=max) as exec:
            futures = [exec.submit(process, **kw) for kw in tasks]
            results = [f.result() for f in as_completed(futures)]
        cost = time() - ti
        return results.count(True), cost

    @staticmethod
    def extend_dir(root_dir, filter=None):
        filter = filter or {}
        include = filter.get('include')
        pathes = []

        def _get_all(src):
            p = Path(src)
            if p.is_dir():
                for sub in p.rglob('*'):
                    _get_all(sub)
            elif p.is_file() and not p.name.startswith('.'):
                pathes.append(str(p.resolve()))

        _get_all(root_dir)
        if not include:
            return pathes

        ret = []
        for path in pathes:
            if not re.search(include, path):
                continue
            ret.append(path)

        return ret

    @staticmethod
    def pack_files(out_path, src_paths=[]):
        with open(out_path, 'w', encoding='utf-8') as f:
            for src_path in src_paths:
                for path in Utils.extend_dir(src_path):
                    try:
                        content = Path(path).read_text(encoding='utf-8')
                        f.write(f"文件:{path}\n代码内容:\n{content}\n")
                    except Exception as e:
                        Utils.print_exc(e, path)

    @staticmethod
    def print_exc(e: Exception, *args):
        if isinstance(e, AssertionError):
            log(e.args[0])
            return

        import traceback
        log(f"{str(e)} {traceback.format_exc()}", *args)

    @staticmethod
    def split_think(text):
        match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
        if not match:
            return text, None

        str = match.group(1).strip()
        ret = re.sub(r"<think>.*?</think>", '', text, flags=re.DOTALL)
        return ret, str

    @staticmethod
    def parse_element(name, src):
        match = re.search(f"<{name}>(.*?)</{name}>", src, re.DOTALL)
        if match and match.group(1):
            return match.group(1).strip()


if __name__ == '__main__':
    path = "/Users/zhenghongwei/work/rom/rom_gservers/layer_logic/server_kingdom/agent"
    doc_content = Utils.pack_files("output/1.md", [path])
