import subprocess as sub
import sys
import os ##importing an entire library to use one command once :sob: ##nvm it gets used multiple times
import getpass as passwd

selectedDesktop = printKnownDesktops()

def printKnownDesktops():
    knownDesktops = ["KDE Plasma", "Xfce"]
    sub.call("clear")
    print("so far we have ")
    for index, knownDesktops in enumerate(knownDesktops, start=1):
        print(f"{index}. {knownDesktops}")
    selectedDesktop = int(input("Which desktop: "))
    match selectedDesktop:
        case "1":
            selectedDesktop = ["plasma", "kde-applications", "konsole"]
            return selectedDesktop
        case "2":
            selectedDesktop = ["xfce4", "xfce4-goodies"]
            return selectedDesktop
        case _:
            print("unkown option")
            printKnownDesktops()



weAreInChroot = sub.run(["systemd-detect-virt", "--chroot"]) ##note: dunno if this will even work lol ##addendum: It does!
pacstrap = ["pacstrap", "-K", "/mnt", ]
pacman = ["pacman", "-Syyu", "--needed", "--noconfirm", ]
installYay = pacman + ["git", "base-devel", "&&", "git", "clone", "https://aur.archlinux.org/yay.git", "&&", "cd", "yay", "&&", "makepkg", "-si", "&&", "cd", "&&", "rm -rf", "yay/"]
bootstrapLinux = pacstrap + ["linux", "linux-firmware", "base", "python", "nano"]
installDesktop = pacman + [selectedDesktop, "plasma-login-manager", "sudo", "grub", "efibootmgr", "os-prober"]
enableItAll = ["systemctl", "enable", "NetworkManager", "plasmalogin", ]
currentDir = os.getcwd()
grubInstall = ["grub-install", "--target=x86_64-efi", "--efi-directory=esp", "--bootloader-id=GRUB"]
makegrubConfig = ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"]
likeThisScriptGetThisScript = ["git", "clone", "https://github.com/ThatOneUltma/ArchAutoInstall.git"]

sub.run(["touch", "install.log"])


"""
========================================
STEP 2 BELOW>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
========================================
"""

if weAreInChroot.returncode == 0:
    username:str = input("What is your username?: ")
    userPassword:str = passwd.getpass(f"What is your password for {username}?: ")
    sub.run(["useradd", username])
    #isUserSudo:str = input(f"is {username} a sudo account?(Y/N)")  ##COMMENTED OUT REMEMBER TO ADD LATER
    #match(isUserSudo.lower()):
    #    case "y":
    #        sub.run(["usermod", "-aG", "wheel", username])
    #        input('Go to the bottom of the file and uncomment "%wheel ALL=(ALL:ALL) ALL" will ya? (Enter to continue)')
    #        sub.run(["visudo", env == editor])
    #        test = sub.run(["sudo", "whoami"])
    #        if str(test.stdout) == "root":
    #            input(f"There was an error with making {username} a superuser! I dunno what since I cant see what you uncommented but hey! you can keep trucking (Enter) or exit the script. (CTRL + C)")
    #            print("Alright, we keep on goin...")
    #    case "n":
    #        print(f"Fine, Its not like {username} wanted to be a stupid superuser anyways *Hmph*")
    #    case _:
    #        print("ok... asuming no becuase thats the easier option right now.")
    sub.run(["su", username])
    print(f"Enter password for {username}")
    sub.run(["passwd"])
    sub.run(installDesktop)
    sub.run(grubInstall)
    sub.run(makegrubConfig)
    sub.run(enableItAll)
    doWeInstallYae = input("Do you want to install yay? (Y/N): ")
    if doWeInstallYae.lower() == "y":
        print("oka")
        sub.run(installYay)
    else:
        print("oka")

    if input("Do you want to reboot now? (Y/N): ").lower() == "y":
        print("Ok, Arch is supposedly installed, goog buy")
        sub.run(["reboot"])
    else:
        print("Ok, Arch is supposedly installed, goog buy")
        sys.exit(0)

"""
========================================
STEP 1 BELOW>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
========================================
"""

sub.run(["lsblk"])
disk = input("Which disk should be used for this install? (just put sd[letter] or nvme[number] ): ")
sanitisedDisk = disk.lower()
match(sanitisedDisk):
    case sanitisedDisk if "nvme" in sanitisedDisk:
        diskPrefix = "n1"
    case sanitisedDisk if "mmcblk" in sanitisedDisk:
        diskPrefix = "p"
    case _:
        diskPrefix = ""
installDisk = "/dev/" + sanitisedDisk
installDiskWithPrefix = installDisk + diskPrefix

def formatDiskAndMakeSwap():
    standardConfig = str(",1G\n,4G\n;")
    formatBootPartition = ["mkfs.fat", "-F", "32", installDiskWithPrefix + "1"]
    makeSwapFile = ["mkswap", installDiskWithPrefix + "2"]
    formatMainPartition = ["mkfs.ext4", installDiskWithPrefix + "3"]
    sub.run(["sfdisk", installDisk], input=standardConfig)
    sub.run(formatBootPartition)
    sub.run(formatMainPartition)
    sub.run(makeSwapFile)

def mountDiskAndEnableSwap():
    mountBoot = ["mount", "--mkdir", installDiskWithPrefix + "1", "/mnt/boot"]
    mountMain = ["mount", installDiskWithPrefix + "3","/mnt"]
    enableSwap = ["swapon", installDiskWithPrefix + "2"]
    sub.run(mountBoot)
    sub.run(enableSwap)
    sub.run(mountMain)

input(f"!! WARNING !! THIS WILL ERASE EVERYTHING ON {installDisk}! [Enter to continue, CTRL + C to exit]")
input(f"!! FINAL WARNING!! THIS IS PERMANENT AND ALL DATA ON {installDisk} WILL BE LOST FOREVER! [Enter to install, CTRL + C to exit]")

formatDiskAndMakeSwap()
mountDiskAndEnableSwap()
sub.run(bootstrapLinux)
sub.run("genfstab", "-U", ">>", "/mnt/etc/fstab")
print("Step one complete! Copying file to chroot environment and continuing from there...")
os.chdir("../")
os.chdir("/mnt")
sub.run(likeThisScriptGetThisScript)
sub.run(["arch-chroot", "-S", "/mnt", "python", "ArchAutoInstall/ArchAutoInstall.py"])
