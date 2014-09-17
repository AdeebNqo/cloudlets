import subprocess
import time
ifconfig = subprocess.Popen(['ifconfig','wlan0','10.10.0.51'])
masq = subprocess.Popen(['systemctl','start','dnsmasq'])
host = subprocess.Popen(['hostapd','/etc/hostapd/hostapd.conf'])
controller = subprocess.Popen(['python2.7','/root/cloudletX/controller.py','-p','9999'])
ifconfig.wait()
masq.wait()
host.wait()
controller.wait()
