import subprocess as sub
import sys

def terminalCommand(ListOfCommands: list):
    exitCode = sub.call(ListOfCommands)
    if exitCode != 0: ##oh that? thats the if statment that holds the entire script together!
        print("!! ERROR  CAUGHT !!")
        print(f"Last executed command: {ListOfCommands}")
       #print(f"Command output: {exitCode.stdout}") get commented bich
        print(f"Return code: {exitCode}")
        return exitCode
        sys.exit(exitCode)
    else:
        return exitCode 


areWeInChroot = terminalCommand(["systemd-detect-virt", "--chroot"]) ##we are all #erbitingdasun
pacstrap = ["pacstrap", "-K", "/mnt", ]
pacman = ["pacman", "-Syyu", "--needed", "--noconfirm", ]
installYay = pacman + ["git", "base-devel", "&&", "git", "clone", "https://aur.archlinux.org/yay.git", "&&", "cd", "yay", "&&", "makepkg", "-si", "&&", "cd", "&&", "rm -rf", "yay/"]
bootstrapLinux = pacstrap + ["linux", "linux-firmware", "base", "python"]
installDesktop = pacman + ["plasma", "kde-applications", "plasma-login-manager", "sudo"]
currentDir = terminalCommand("pwd")

## im not making an entire function for something that only needs to run once broh
print("Checking for updates...")
terminalCommand(["pacman", "-Syy", "--noconfirm", "--needed", "git"])
terminalCommand(["git", "pull", "https://github.com/ThatOneUltma/ArchAutoInstall.git"])



if areWeInChroot == 0:
    username = input("What is your username?: ")
    userPassword = input(f"What is your password for {username}?: ")
    isUserSudo = input(f"is {username} a sudo account?")
    terminalCommand(["useradd", username])
    terminalCommand(["su", username])
    terminalCommand(["passwd", password])
    
    terminalCommand(installDesktop)
    terminalCommand(installYay)


terminalCommand("lsblk")
disk = input("Which disk should be used for this install? (just put sd[letter] or nvme[number] ): ")
sanitisedDisk = disk.lower()
if "nvme" in sanitisedDisk:
    diskPrefix = "n1p"
else:
    diskPrefix = ""

installDisk = "/dev/" + sanitisedDisk + diskPrefix

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


terminalCommand("lsblk")
input("Does everything look right? [HIT ENTER IF IT DOES OTHERWISE EXIT (CTRL + C) AND SUBMIT AN ISSUE!]")
terminalCommand(bootstrapLinux)
print("Step one complete! Copying file to chroot environment and continuing from there...")
terminalCommand(["cp", currentDir + "ArchAutoInstall.py", "/mnt/"])
terminalCommand(["arch-chroot" "/mnt", "python", "ArchAutoInstall.py"])
