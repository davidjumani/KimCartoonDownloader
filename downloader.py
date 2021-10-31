#!/usr/bin/env python3

import json
import os
import requests
import sys
import traceback
from clint.textui import progress
from concurrent.futures import ThreadPoolExecutor

class Downlaoder :

    def __init__(self, workers=3, quality='720p'):
        self.workers = workers
        self.quality = quality

    def get_download_link(self, url, name) :
        suffix = url.split('/')[-1]
        response = requests.post('https://www.luxubu.review/api/source/' + suffix, {}).json()
        # print json.dumps(response)

        link = [x for x in response['data'] if self.quality in x['label']]
        if len(link) == 0 :
            print("WARN : Could not get %s version of %s" %(self.quality, name))
            link = response['data'][-1]
        else :
            link = link[0]
        print("Got %s version of %s" %(link['label'], name))
        return link['file']


    def download_file(self, path, url) :
        try :
            wip_path = path + '.wip'
            if os.path.exists(wip_path):
                print("%s partially downladed, redownloading" %(wip_path))
                os.remove(wip_path)
            print("Downloading %s" %(path))
            r = requests.get(url, stream=True)
            with open(wip_path, 'wb') as f:
                total_length = int(r.headers.get('content-length'))
                for chunk in progress.bar(r.iter_content(chunk_size=1024), label=path.ljust(70), expected_size=(total_length/1024) + 1):
                    if chunk:
                        f.write(chunk)
                        f.flush()
            os.rename(wip_path, path)
            print("COMPLETED %s" %(path))
        except Exception as e :
            print("FAILED %s" %(path))
            if os.path.exists(wip_path):
                os.remove(wip_path)

    def task(self, name, url, dirname) :
        try :
            path = dirname + '/' + name
            if '.mp4' not in path :
                path = path + '.mp4'
            if os.path.exists(path):
                print("%s exists, skipping" %(name))
            else :
                url = self.get_download_link(url, name)
                if url is None :
                    return
                self.download_file(path, url)
        except Exception as e :
            print(e)
            traceback.print_exc()

    def download(self, data, dirname) :
        print("Downloading %d files" %(len(data)))
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            for name in sorted(data) :
                executor.submit(self.task, name, data[name], dirname)


def main() :
    filename = sys.argv[1]
    qual = '720p'
    if len(sys.argv) > 2 :
        qual = sys.argv[2]

    data = {}
    max_workers = 3
    with open(filename) as file :
        data = json.load(file)

    dirname = filename.replace('.json', '')
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    d = Downlaoder(max_workers)
    d.download(data, dirname)

if __name__ == "__main__" :
    main()
