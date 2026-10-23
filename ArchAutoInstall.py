import subprocess as sub
import sys
import os ##importing an entire library to use one command once :sob:

areWeInChroot = sub.run(["systemd-detect-virt", "--chroot"]) ##note: dunno if this will even work lol ##addendum: It does!

sub.run(["lsblk"])
disk = input("Which disk should be used for this install? (just put sd[letter] or nvme[number] ): ")
sanitisedDisk = disk.lower()
match(sanitisedDisk):
    case sanitisedDisk if "nvme" in sanitisedDisk:
        diskPrefix = "n1p"
    case sanitisedDisk if "mmcblk" in sanitisedDisk:
        diskPrefix = "p"
    case _:
        diskPrefix = ""
installDisk = "/dev/" + sanitisedDisk + diskPrefix

def terminalCommand(ListOfCommands: list): ##horrible nesting remind me to KMS later
    exitCode = sub.run(ListOfCommands)
    if exitCode.returncode != 0: ##oh that? thats the if statment that holds the entire script together!
        with open("install.log", "a") as logFile:
            print("!! ERROR  CAUGHT !!", file=logFile)
            print(f"Last executed command: {ListOfCommands}", file=logFile)
            print(f"Command output: {exitCode.stdout}", file=logFile)
            print(f"Return code: {exitCode.returncode}", file=logFile)
            #terminalCommand(["umount", "/mnt"])
            #terminalCommand(["umount", "/mnt/boot"])
            #terminalCommand(["swapoff", installDisk + "2"])
            sys.exit(exitCode.returncode)
    else:
        with open("install.log", "a") as logFile
            print(f"No errors with {ListOfCommands}", file=logFile)
            return any


terminalCommand(["touch", "install.log"])



pacstrap = ["pacstrap", "-K", "/mnt", ]
pacman = ["pacman", "-Syyu", "--needed", "--noconfirm", ]
installYay = pacman + ["git", "base-devel", "&&", "git", "clone", "https://aur.archlinux.org/yay.git", "&&", "cd", "yay", "&&", "makepkg", "-si", "&&", "cd", "&&", "rm -rf", "yay/"]
bootstrapLinux = pacstrap + ["linux", "linux-firmware", "base", "python"]
installDesktop = pacman + ["plasma", "kde-applications", "plasma-login-manager", "sudo"]
getThisScript = ["git", "clone", "https://github.com/ThatOneUltma/ArchAutoInstall.git"]
currentDir = str(terminalCommand("pwd"))

## im not making an entire function for something that only needs to run once broh
print("Checking for updates...")
terminalCommand(["pacman", "-Syy", "--noconfirm", "--needed", "git"])
terminalCommand(["git", "pull", "https://github.com/ThatOneUltma/ArchAutoInstall.git"])

"""
========================================
STEP 2 BELOW
========================================
"""

if areWeInChroot == 0:
    username = input("What is your username?: ")
    userPassword = input(f"What is your password for {username}?: ")
    isUserSudo = input(f"is {username} a sudo account?")
    terminalCommand(["useradd", username])
    terminalCommand(["su", username])
    terminalCommand(["passwd", userPassword])
    
    terminalCommand(installDesktop)
    terminalCommand(installYay)

"""
========================================
STEP 1 BELOW
=======================================
"""

def formatDiskAndMakeSwap():
    partitionSetup = ["echo" "-e" "',1G\n,4G\n;'" "|" "sfdisk" + installDisk]
    formatBootPartition = ["mkfs.fat", "-F", "32", installDisk + "1"]
    makeSwapFile = ["mkswap", installDisk + "2"]
    formatMainPartition = ["mkfs.ext4", installDisk + "3"]
    terminalCommand(formatBootPartition)
    terminalCommand(formatMainPartition)
    terminalCommand(makeSwapFile)

def mountDiskAndEnableSwap():
    mountBoot = ["mount", "--mkdir", installDisk + "1", "/mnt/boot"]
    mountMain = ["mount", installDisk + "3", "/mnt"]
    enableSwap = ["swapon", installDisk + "2"]
    terminalCommand(mountBoot)
    terminalCommand(enableSwap)
    terminalCommand(mountMain)

input(f"!! WARNING !! THIS WILL ERASE EVERYTHING ON {installDisk}! [Enter to continue, CTRL + C to exit]")
input(f"!! FINAL WARNING!! THIS IS PERMANENT AND ALL DATA ON {installDisk} WILL BE LOST FOREVER! [Enter to install, CTRL + C to exit]")

formatDiskAndMakeSwap()
mountDiskAndEnableSwap()
terminalCommand("lsblk")
input("Does everything look right? [HIT ENTER IF IT DOES OTHERWISE EXIT (CTRL + C) AND SUBMIT AN ISSUE!]")
terminalCommand(bootstrapLinux)
print("Step one complete! Copying file to chroot environment and continuing from there...")
print(currentDir + "ArchAutoInstall.py")
os.chdir("/mnt/")
terminalCommand(getThisScript)
terminalCommand(["arch-chroot", "/mnt", "python", "ArchAutoInstall.py"])
