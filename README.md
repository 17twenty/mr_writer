mr_writer
=========

Simple image writer hackjob to make Admin life easier

Note: This was developed on Fedora 18 and as such it uses /var/run/mount/utab to read removable media. A quick fix for Ubuntu devices is to read from /etc/mtab instead and add a check for /media.

So....

        f = open("/run/mount/utab").readlines()
        
        for drive in os.listdir("/dev/"):
            if drive.startswith("sd") and drive.isalpha():
                for line in f:
                    if drive in line:
                        self.drive_list.append("/dev/" + drive)
                        
becomes:
                        
        f = open("/etc/mtab").readlines()
        
        for drive in os.listdir("/dev/"):
            if drive.startswith("sd") and drive.isalpha():
                for line in f:
                    if drive in line and "/media" in line:
                        self.drive_list.append("/dev/" + drive)


Note
-----
This project leverages the SETUID bit in the helper C executable - it WON'T work if you have your FS mounted as nosuid and will fail with permission errors!
