import subprocess as sub

whatDoesThisOutput = sub.run(["systemd-detect-virt", "--chroot"])\

print(whatDoesThisOutput)
