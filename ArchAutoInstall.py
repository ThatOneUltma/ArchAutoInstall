import subprocess as sub

pacstrap = ["pacstrap", "-K", "/mnt", ]
pacman = ["pacman", "-Syyu", "--needed", "--noconfirm", ]
installYay = pacman + ["git", "base-devel", "&&", "git", "clone", "https://aur.archlinux.org/yay.git", "&&", "cd", "yay", "&&", "makepkg", "-si", "&&", "cd", "&&", "rm -rf", "yay/"]
bootstrapLinux = pacstrap + ["linux", "linux-firmware", "base", "python"]
installDesktop = pacman + ["plasma", "kde-applications", "plasma-login-manager"]
currentDir = sub.call("pwd")

print("Checking for updates...")
sub.call(["pacman", "-Syy", "--noconfirm", "--needed", "git"])
sub.call(["git", "pull", "https://github.com/ThatOneUltma/ArchAutoInstall.git"])


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
mountBoot = ["mount", "--mkdir", installDisk + "1", "/mnt/boot"]
mountMain = ["mount", installDisk + "3", "/mnt"]
enableSwap = ["swapon", installDisk + "2"]

input(f"!! WARNING !! THIS WILL ERASE EVERYTHING ON {installDisk}! [Enter to continue, CTRL + C to exit]")
input(f"!! FINAL WARNING!! THIS IS PERMANENT AND ALL DATA ON {installDisk} WILL BE LOST FOREVER! [Enter to install, CTRL + C to exit]")
sub.call(formatBootPartition)
sub.call(formatMainPartition)
sub.call(makeSwapFile)
sub.call(mountBoot)
sub.call(enableSwap)
sub.call(mountMain)
sub.call("lsblk")
input("Does everything look right? [HIT ENTER IF IT DOES OTHERWISE EXIT (CTRL + C) AND SUBMIT AN ISSUE!]")
sub.call(bootstrapLinux)
print("Step one complete! Copying file to chroot environment and continuing from there...")
sub.call(["cp", currentDir + "ArchAutoInstall.py", "/mnt/"])
sub.call(["arch-chroot" "/mnt", "python", "ArchAutoInstall.py"])

#sub.call(installDesktop)
