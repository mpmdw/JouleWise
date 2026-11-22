"""Isolate two synthetic releases by replaying an ext4 image on one loop device.

The two images begin with the same filesystem metadata. Mounting each at the
same location and on the same loop device preserves the registered path and
inode and device numbers. The first image retains its claim and publication.
The comparator sees copies of the second image's actual files.
"""

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


LOOK = "lm-ctl-01"


class Images:
    def __init__(self, world):
        self.mount = Path(os.environ["CTL_PAIR_MOUNT"])
        self.loop = os.environ["CTL_PAIR_LOOP"]
        self.normal = self.mount.parent / "original.ext4"
        self.clone = self.mount.parent / "clone.ext4"
        if (self.mount.name != "mounted" or not self.mount.is_mount()
                or not self.mount.parent.name.startswith("ctl-pair.")
                or not world.is_relative_to(self.mount)
                or not re.fullmatch(r"/dev/loop[0-9]+", self.loop)):
            raise ValueError("paired fixture mount is outside the synthetic bench")
        self._attached_to(self.normal)

    def _attached_to(self, image):
        actual = subprocess.check_output(
            ["sudo", "-n", "losetup", "--noheadings", "--output", "BACK-FILE", self.loop],
            text=True,
        ).strip()
        if actual != str(image):
            raise ValueError("paired fixture loop device differs")

    def detach(self, image):
        self._attached_to(image)
        self._run("umount", str(self.mount))
        self._run("losetup", "-d", self.loop)

    def attach(self, image):
        self._run("losetup", self.loop, str(image))
        self._run("mount", "-o", "nosuid,nodev", self.loop, str(self.mount))

    @staticmethod
    def _run(*operation):
        subprocess.run(["sudo", "-n", *operation], check=True)


def _copy_state(source, target):
    for name in ("private", "public"):
        shutil.copytree(source/name, target/name, dirs_exist_ok=True)
    for name in ("events.jsonl", "joined-observed.json", "kernel-observed.json", "registered-public.json"):
        if (source/name).is_file():
            shutil.copy2(source/name, target/name)


def clone_fresh(world, bench):
    images = Images(world)
    if images.clone.exists():
        raise FileExistsError(images.clone)
    images.detach(images.normal)
    try:
        shutil.copyfile(images.normal, images.clone)
    finally:
        images.attach(images.normal)
    _copy_state(bench, bench.with_name("clone"))
    return 0


def run_zero(driver, world, proxy):
    images = Images(world)
    real_bench = proxy.with_name("bench")
    with tempfile.TemporaryDirectory(dir=images.mount.parent) as folder:
        saved = Path(folder)
        images.detach(images.normal)
        try:
            images.attach(images.clone)
            try:
                result = subprocess.run([driver, "stage2", str(world), str(real_bench),
                                         "observe_zero_h_on_clone"], check=False)
                _copy_state(real_bench, saved)
            finally:
                images.detach(images.clone)
        finally:
            images.attach(images.normal)
        _copy_state(saved, proxy)
        return result.returncode
