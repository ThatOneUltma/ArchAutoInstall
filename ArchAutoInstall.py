import subprocess as sub
import sys
import os ##importing an entire library to use one command once :sob:
import getpass as passwd

weAreInChroot = sub.run(["systemd-detect-virt", "--chroot"]) ##note: dunno if this will even work lol ##addendum: It does!
pacstrap = ["pacstrap", "-K", "/mnt", ]
pacman = ["pacman", "-Syyu", "--needed", "--noconfirm", ]
installYay = pacman + ["git", "base-devel", "&&", "git", "clone", "https://aur.archlinux.org/yay.git", "&&", "cd", "yay", "&&", "makepkg", "-si", "&&", "cd", "&&", "rm -rf", "yay/"]
bootstrapLinux = pacstrap + ["linux", "linux-firmware", "base", "python", "nano"]
installDesktop = pacman + ["plasma", "kde-applications", "plasma-login-manager", "sudo"]
enableShit = ["systemctl", "enable", "NetworkManager", "plasmalogin", ]
currentDir = os.getcwd()
editor = "EDITOR=nano"
bootConfigFile: str = str(["default  arch.conf\n", "timeout  4\n", "console-mode max\n", "editor   no"])
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

def terminalCommand(ListOfCommands: list, text: bool = True, input = None, env = None): ##horrible nesting remind me to KMS later
    exitCode = sub.run(ListOfCommands, text=text, input=input, env=env)
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
        with open("install.log", "a") as logFile:
            print(f"No errors with {ListOfCommands}", file=logFile)
            return any


terminalCommand(["touch", "install.log"])

"""
========================================
STEP 2 BELOW>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
========================================
"""
print(f"Chroot detection returncode = {weAreInChroot.returncode}")
if weAreInChroot.returncode == 0:
    username:str = input("What is your username?: ")
    userPassword:str = passwd.getpass(f"What is your password for {username}?: ")
    terminalCommand(["useradd", username])
    #isUserSudo:str = input(f"is {username} a sudo account?(Y/N)")  ##COMMENTED OUT REMEMBER TO ADD LATER
    #match(isUserSudo.lower()):
    #    case "y":
    #        terminalCommand(["usermod", "-aG", "wheel", username])
    #        input('Go to the bottom of the file and uncomment "%wheel ALL=(ALL:ALL) ALL" will ya? (Enter to continue)')
    #        terminalCommand(["visudo", env == editor])
    #        test = sub.run(["sudo", "whoami"])
    #        if str(test.stdout) == "root":
    #            input(f"There was an error with making {username} a superuser! I dunno what since I cant see what you uncommented but hey! you can keep trucking (Enter) or exit the script. (CTRL + C)")
    #            print("Alright, we keep on goin...")
    #    case "n":
    #        print(f"Fine, Its not like {username} wanted to be a stupid superuser anyways *Hmph*")
    #    case _:
    #        print("ok... asuming no becuase thats the easier option right now.")
    terminalCommand(["bootctl", "install"])
    with open("/boot/loader/loader.conf", "w") as bootConfig:
        bootConfig.write(bootConfigFile)
        print(f"this should have written {bootConfigFile}")
        print("this is what was written")
        terminalCommand(["cat", "/boot/loader/loader.conf"])
        input("Break tiem!")
    terminalCommand(["su", username])
    terminalCommand(["passwd"])
    terminalCommand(installDesktop)
    terminalCommand(enableShit)
    doWeInstallYae = input("Do you want to install yay? (Y/N): ")
    match(doWeInstallYae.lower()):
        case "y":
            terminalCommand(installYay)
        case "n":
            print("oka")
    if input("Do you want to reboot now? (Y/N): ").lower() == "y":
        print("Ok, Arch is supposedly installed, goog buy")
        terminalCommand(["reboot"])
    else:
        print("Ok, Arch is supposedly installed, goog buy")
        sys.exit(0)

"""
========================================
STEP 1 BELOW>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
========================================
"""

def formatDiskAndMakeSwap():
    standardConfig = str(",1G\n,4G\n;")
    formatBootPartition = ["mkfs.fat", "-F", "32", installDiskWithPrefix]
    makeSwapFile = ["mkswap", installDiskWithPrefix]
    formatMainPartition = ["mkfs.ext4", installDiskWithPrefix]
    terminalCommand(["sfdisk", installDisk], input=standardConfig)
    terminalCommand(formatBootPartition)
    terminalCommand(formatMainPartition)
    terminalCommand(makeSwapFile)

def mountDiskAndEnableSwap():
    mountBoot = ["mount", "--mkdir", installDiskWithPrefix, "/mnt/boot"]
    mountMain = ["mount", installDiskWithPrefix,"/mnt"]
    enableSwap = ["swapon", installDiskWithPrefixWithPrefix]
    terminalCommand(mountBoot)
    terminalCommand(enableSwap)
    terminalCommand(mountMain)

input(f"!! WARNING !! THIS WILL ERASE EVERYTHING ON {installDisk}! [Enter to continue, CTRL + C to exit]")
input(f"!! FINAL WARNING!! THIS IS PERMANENT AND ALL DATA ON {installDisk} WILL BE LOST FOREVER! [Enter to install, CTRL + C to exit]")

formatDiskAndMakeSwap()
mountDiskAndEnableSwap()
terminalCommand(["lsblk"])
input("Does everything look right? [HIT ENTER IF IT DOES OTHERWISE EXIT (CTRL + C) AND SUBMIT AN ISSUE!]")
terminalCommand(bootstrapLinux)
print("Step one complete! Copying file to chroot environment and continuing from there...")
os.chdir("../")
os.chdir("/mnt")
terminalCommand(["git", "clone", "https://github.com/ThatOneUltma/ArchAutoInstall.git"])
terminalCommand(["pwd"])
terminalCommand(["ls"])
input("")
terminalCommand(["arch-chroot", "-S", "/mnt", "python", "ArchAutoInstall/ArchAutoInstall.py"])
