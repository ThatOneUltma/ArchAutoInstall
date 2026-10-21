import subprocess as sub

pacstrap = ["pacstrap", "-K", "/mnt", ]
pacman = ["pacman", "-Syyu", "--needed", "--noconfirm", ]
installYay = pacman + ["git", "base-devel", "&&", "git", "clone", "https://aur.archlinux.org/yay.git", "&&", "cd", "yay", "&&", "makepkg", "-si", "&&", "cd", "&&", "rm -rf", "yay/"]
bootstrapLinux = pacstrap + ["linux", "linux-firmware", "base"]
installDesktop = pacman + ["plasma", "kde-applications", "plasma-login-manager"]


sub.call("lsblk")
disk = input("Which disk should be used for this install? (just put sd[letter] or nvme[number] ): ")
sanitisedDisk = disk.lower()
if "nvme" in sanitisedDisk:
    diskPrefix = "n1p"
else:
    diskPrefix = ""

installDisk = "/dev/" + sanitisedDisk + diskPrefix
partitionSetup = ["echo" "-e" "',1G\n,4G\n;'" "|" "sfdisk" + installDisk]

formatBootPartition = ["mkfs.fat", "-F", "32", installDisk + "1"]
makeSwapFile = ["mkswap", installDisk + "2"]
formatMainPartition = ["mkfs.ext4", installDisk + "3"]
mountDisk = ["mount", "--mkdir", installDisk + "1", "/mnt/boot", "&&", "mount", installDisk + "3", "/mnt", "&&", "swapon", installDisk + "2"]

sub.call(bootstrapLinux)
sub.call(installDesktop)