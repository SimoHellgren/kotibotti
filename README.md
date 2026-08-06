# Running kotibotti as a systemd user service

1. Install with `pipx install git+https://github.com/SimoHellgren/kotibotti.git`

2. Copy the env template and fill in the real token:
   ```bash
   mkdir -p ~/.config/kotibotti
   cp systemd/kotibotti.env.example ~/.config/kotibotti/kotibotti.env
   chmod 600 ~/.config/kotibotti/kotibotti.env
   $EDITOR ~/.config/kotibotti/kotibotti.env
   ```
3. Install the unit:
   ```bash
   mkdir -p ~/.config/systemd/user
   cp systemd/kotibotti.service ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable --now kotibotti.service
   ```
4. Enable lingering so the service keeps running after logout/reboot without an active login session:
   ```bash
   loginctl enable-linger "$USER"
   ```
5. Check logs: `journalctl --user -u kotibotti -f`
