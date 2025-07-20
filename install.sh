#!/bin/bash
set -e

# 1. Create venv with python3.11 if not exists
if [ ! -d "$HOME/electrum-venv" ]; then
  python3.11 -m venv $HOME/electrum-venv
fi

# 2. Activate venv
source $HOME/electrum-venv/bin/activate

# 3. Install Electrum from source if not already installed
if ! electrum --version >/dev/null 2>&1; then
  if [ ! -d "Electrum-4.4.5" ]; then
    wget https://download.electrum.org/4.4.5/Electrum-4.4.5.tar.gz
    tar -xvf Electrum-4.4.5.tar.gz
  fi
  cd Electrum-4.4.5
  pip install '.['fast']'
  cd ..
fi

# 4. Install torch first (compatible with python3.11 and audiocraft)
pip install torch==2.1.0

# 5. Install all other Python dependencies except torch, audiocraft, and julius
grep -v -E '^(torch|audiocraft|julius)' requirements.txt > requirements-no-torch.txt
pip install -r requirements-no-torch.txt

# 6. Install audiocraft and julius with --no-deps
pip install --no-deps audiocraft julius

# 7. Create run_app.sh
cat <<EOS > $HOME/PocketFlow/run_app.sh
#!/bin/bash
source \$HOME/electrum-venv/bin/activate
cd \$HOME/PocketFlow
python main.py
EOS
chmod +x $HOME/PocketFlow/run_app.sh

# 8. Create systemd service file
SERVICE_FILE=/etc/systemd/system/pocketflow.service
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=PocketFlow Email Agent and BTC Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/PocketFlow
ExecStart=$HOME/PocketFlow/run_app.sh
Restart=on-failure
Environment=BTC_SHARED_PATH=$HOME/PocketFlow/shared.yaml
EnvironmentFile=$HOME/PocketFlow/.env

[Install]
WantedBy=multi-user.target
EOF

# 9. Reload and enable the service
sudo systemctl daemon-reload
sudo systemctl enable pocketflow

# 10. Print instructions
cat <<EOM

---
Install complete!

- To start the service: sudo systemctl start pocketflow
- To check status: sudo systemctl status pocketflow
- To view logs: journalctl -u pocketflow -f
- To run manually: source ~/electrum-venv/bin/activate && python main.py

BTC Wallet Setup:
- Restore your wallet with: source ~/electrum-venv/bin/activate && electrum restore "<your seed>"
- Start the daemon: electrum daemon -d

---
EOM 

# Ensure requests is installed for BTC price fetching
pip install requests

echo "\n---\nTo enable automatic token crediting from BTC payments, ensure Electrum's daemon is running:"
echo "    electrum daemon start"
echo "    electrum daemon load_wallet"
echo "\nTo run the BTC-to-token crediting script manually:"
echo "    PYTHONPATH=. python3 utils/credit_tokens_from_btc.py"
echo "\nTo automate, add this line to your crontab (every 5 minutes):"
echo "    */5 * * * * cd $(pwd) && PYTHONPATH=. python3 utils/credit_tokens_from_btc.py >> btc_credit.log 2>&1" 

# Ensure python-dotenv is installed for Electrum startup script
pip install python-dotenv

echo "\n---\nTo start Electrum daemon and load your wallet using your .env seed, run:"
echo "    PYTHONPATH=. python3 utils/start_electrum_with_env.py" 