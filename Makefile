install:
	cp ./smart-fan-control.py /usr/local/sbin/smart-fan-control
	chmod +x /usr/local/sbin/smart-fan-control

install-launchd:
	cp ./com.github.darvelo.smart-fan-control.plist /Library/LaunchDaemons/
	launchctl unload -w /Library/LaunchDaemons/com.github.darvelo.smart-fan-control.plist
	launchctl load -w /Library/LaunchDaemons/com.github.darvelo.smart-fan-control.plist
