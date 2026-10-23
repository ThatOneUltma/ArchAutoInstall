umount /mnt
umount /mnt/boot
swapoff /dev/nvme0n1p2
git pull https://github.com/ThatOneUltma/ArchAutoInstall.git
python ArchAutoInstall.py
