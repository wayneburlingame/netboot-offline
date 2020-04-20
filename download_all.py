import yaml
import pathlib
import requests
import time
import os.path
import json
from tqdm import tqdm
from nbexceptions import links_exceptions


DOWNLOAD_BASE_URL = "https://github.com/netbootxyz"
NETBOOTXYZ_DIR = ".."
DEST_DIR = "./out"
TEMP_DIR = "./tmp"

epcfg = yaml.safe_load(open(NETBOOTXYZ_DIR + "/endpoints.yml").read())
oscfg = yaml.safe_load(open(NETBOOTXYZ_DIR + "/roles/netbootxyz/defaults/main.yml").read())
uocfg = yaml.safe_load(open(NETBOOTXYZ_DIR + "/user_overrides.yml").read())

# Actual download
# TODO: we need to have a mechanism to select which operating system we want to download
# we can't download the whole world
def download_files(only_show_links):
    # Download external links (such as AVG)
    for keyname in ["releases", "utilitiesefi", "utilitiespcbios"]:
        for osname in oscfg[keyname]:
            if not "enabled" in oscfg[keyname][osname] or not oscfg[keyname][osname]["enabled"]:
                # System disabled
                continue

            overridekey = keyname.replace("releases", "release") + "_overrides"
            if overridekey in uocfg and osname in uocfg[overridekey] and "enabled" in uocfg[overridekey][osname] and not uocfg[overridekey][osname]["enabled"]:
                # User disabled
                continue

            if "util_path" in oscfg[keyname][osname]:
                # Download this
                fileurl = oscfg[keyname][osname]["util_path"]
                basefname = fileurl.split("/")[-1]
                destdir = "%s/__external/%s/%s/" % (DEST_DIR, keyname, osname)
                if only_show_links:
                    print(fileurl)
                else:
                    download_with_progress(fileurl, destdir, basefname)
                continue
    
            # Download endpoints (netboot.xyz generated files)
            found = False
            for i in epcfg["endpoints"]:
                ep = epcfg["endpoints"][i]
                if ep["os"] != osname:
                    continue
                found = True
                
                destdir = DEST_DIR + ep["path"]

                for fname in ep["files"]:
                    fileurl = DOWNLOAD_BASE_URL + ep["path"] + fname

                    if only_show_links:
                        print(fileurl)
                    else:
                        download_with_progress(fileurl, destdir, fname)

            if not found:
                # This should not happen
                print("Error: OS %s not found in endpoints" % osname)
                exit(1)
                    


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def download_with_progress(fileurl, destdir, destfname):
    destfileobj = pathlib.Path(destdir + destfname)
    if destfileobj.is_file():
        print("%s File already downloaded, skipping" % fileurl)
        return
    
    pathlib.Path(destdir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)
    tempfile = "%s/%s" % (TEMP_DIR, destfname)

    try:
        os.unlink(tempfile)
    except:
        pass
    
    print(fileurl)
    r = requests.get(fileurl, allow_redirects=True, stream=True)
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte
    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(tempfile, 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()

    if total_size != 0 and t.n != total_size:
        print("ERROR, something went wrong with file %s" % destfile)
        os.unlink(tempfile)
    else:
        os.rename(tempfile, destdir + destfname)


def download_exceptions(only_show_links):
    links = links_exceptions()
    for linkset in links:
        for fileurl in linkset:
            outfile = linkset[fileurl]
            destdir = "/".join(outfile.split("/")[:-1]) + "/"
            fname = outfile.split("/")[-1]
            if only_show_links:
                print(fileurl)
            else:
                download_with_progress(fileurl, DEST_DIR + destdir, fname)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Create a full offline copy of Netboot.xyz images")
    parser.add_argument("--links", dest="links", action="store_const", const=True, default=False, help="Dump all links without download them")

    args = parser.parse_args()

    download_files(args.links)
    download_exceptions(args.links)
