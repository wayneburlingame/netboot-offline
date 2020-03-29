# Netboot.xyz full offline storage

Project URL: https://gitlab.com/Enrico204/netboot-offline

These bunch of scripts will prepare a full offline copy of [Netboot.xyz](https://github.com/netbootxyz/netboot.xyz/).
I like `netboot.xyz`, and I prepared this script to have an offline copy when I don't have access to a broadband network
capable of network booting.

**Important**: this script will download all images/ISOs as it was meant to create a personal copy, however some images
**cannot be redistribuited** (even if they're freely downloadable). It's your responsibility to enable only images that
you're authorized to redistribuite.

The status of this project is: work in progress / alpha

# Requirements

Free space:

* Operating systems (releases): ?
* Utilities (EFI/BIOS): ~8.5 GB

Also, it needs Python 3 (tested with `3.7`). You to install all dependencies in the `requirements.txt` file
(I suggest you to use a `virtualenv` for this):

```sh
pip install -r requirements.txt
```

# Usage

## Step 1: Prepare Netboot.xyz

First, you need to download the official `netboot.xyz` code:

```sh
git clone https://github.com/netbootxyz/netboot.xyz.git /opt/netboot.xyz
```

Now you need to execute `create_overrides.py`. See `create_overrides.py --help` for available options.

## Step 2: Download everything

Customize the `user_overrides.yml` to enable/disable what you want to download and show in the `netboot.xyz` menu, then:

```sh
python download_all.py
```

## Step 3: Generate Netboot.xyz files

To generate files for `netboot.xyz` you can use the standard way:

```sh
ansible-playbook -i inventory site.yml
```

or the Docker way:

```sh
docker build -t localbuild -f Dockerfile-build .
docker run --rm -it -v $(pwd):/buildout localbuild
```

At the end you'll have the output inside `buildout/` (docker way) or directly inside `/var/www/html` (standard way).

Now you can boot from PXE using images inside `buildout/ipxe/`. For example, if you want to use TFTP, you can use
`sudo in.tftpd -L -s buildout/ipxe/` and you can configure your DHCP server to serve the file `netboot.xyz.kpxe`. Refer to the
[official guide](https://netboot.xyz/booting/tftp/).

# License

See [LICENSE](LICENSE) file.

# More

I've added my personal Dockerfile, which I think is more optimized for rebuilds (eg. when testing `user_overrides.yml` options).
The image should be builded by issuing this command inside the `netboot.xyz` repository root directory:

```sh
docker build -t netbootbuilder -f /path/to/this/repo/Dockerfile.netbootxyz .
```

Then executed as:

```sh
docker run --rm -it -v /path/to/netboot.xyz/user_overrides.yml:/ansible/user_overrides.yml -v /path/to/buildout:/var/www/html netbootbuilder
```
