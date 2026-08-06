# Running kotibotti as a systemd user service

1. Install with `pipx install git+https://github.com/SimoHellgren/kotibotti.git`

2. Create env-file, copy contents from the [example file](systemd/kotibotti.env.example) and add bot token:
   ```bash
   mkdir -p ~/.config/kotibotti
   touch ~/.config/kotibotti/kotibotti.env
   chmod 600 ~/.config/kotibotti/kotibotti.env
   $EDITOR ~/.config/kotibotti/kotibotti.env
   ```
3. Create unit file, copy contents from the [example file](systemd/kotibotti.service) and install the unit:
   ```bash
   mkdir -p ~/.config/systemd/user
   touch ~/.config/systemd/user/
   $EDITOR ~/.config/systemd/user/kotibotti.service
   systemctl --user daemon-reload
   systemctl --user enable --now kotibotti.service
   ```
4. Enable lingering so the service keeps running after logout/reboot without an active login session:
   ```bash
   loginctl enable-linger "$USER"
   ```
5. Check logs: `journalctl --user -u kotibotti -f`
