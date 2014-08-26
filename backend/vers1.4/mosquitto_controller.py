#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This is the class that starts mosquitto. it exists
# so that we can be able to capture client (dis)connections.
#
# "I did not attend his funeral, but I sent a nice letter saying
#  I approved of it."
#  -Mark Twain
#
import subprocess
def main():
    proc = subprocess.Popen(['mosquitto -p 9999'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while proc.returncode is None:
        # handle output by direct access to stdout and stderr
        line = proc.stderr.read()
        print('line: '+line)
        # set returncode if the process has exited
        proc.poll()
if __name__=='__main__':
    main()