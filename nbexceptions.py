
def links_exceptions():
    substs = []
    substs.append(flatcar_links())
    return substs


def fix_exceptions(netbootroot, baseurl):
    flatcar_fix(netbootroot, baseurl)


# FLATCAR
def flatcar_fix(netbootroot, baseurl):
    with open(netbootroot + "/roles/netbootxyz/templates/menu/flatcar.ipxe.j2", "r+") as f:
        content = f.read().replace("http://${release}.release.flatcar-linux.net/amd64-usr/current", baseurl + "/flatcar/${release}")
        f.seek(0)
        f.write(content)
        f.truncate()

def flatcar_links():
    retmap = {}
    for release in ["stable", "beta", "alpha", "edge"]:
        for fname in ["flatcar_production_pxe.vmlinuz", "flatcar_production_pxe_image.cpio.gz"]:
            retmap["http://%s.release.flatcar-linux.net/amd64-usr/current/%s" % (release, fname)] = "/flatcar/%s/%s" % (release, fname)
    return retmap

