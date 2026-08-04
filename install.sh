#!/usr/bin/env bash
# ==============================================================================
# Japan Stock Market Prediction Engine - 1-Click Installer
# ==============================================================================

set -e

echo "======================================================================"
echo "  Installing Japan Stock Market Prediction Engine..."
echo "======================================================================"

mkdir -p bin

# 1. Compile SaC Engine
if command -v sac2c &> /dev/null; then
    echo "[1/4] Compiling SaC Engine (sac2c -O3)..."
    sac2c -O3 src/sac_pipeline.sac -o bin/sac_pipeline
    echo "  -> SaC binary created: bin/sac_pipeline"
fi

# 2. Compile Chapel Engine
if command -v chpl &> /dev/null; then
    echo "[2/4] Compiling Chapel Engine (chpl)..."
    chpl src/chapel_chopper.chpl -o bin/chapel_chopper
    echo "  -> Chapel binary created: bin/chapel_chopper"
fi

# 3. Install Python Dependencies
echo "[3/4] Installing Python Package..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi
pip install -e .

# 4. Create Global CLI Commands
echo "[4/4] Registering 'predict-japan' command..."
cat << 'EOF' > bin/predict-japan
#!/usr/bin/env bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi
export LD_LIBRARY_PATH="$(nix-build '<nixpkgs>' -A stdenv.cc.cc.lib --no-out-link 2>/dev/null)/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"
exec python "$SCRIPT_DIR/src/cli.py" "$@"
EOF

chmod +x bin/predict-japan
cp bin/predict-japan bin/non-neumann

echo "======================================================================"
echo "  INSTALLATION COMPLETE!"
echo "  Command to run predictions:"
echo "    ./bin/predict-japan predict --ticker ALL --time 09:30"
echo "  Command to start intraday daemon:"
echo "    ./bin/predict-japan daemon"
echo "======================================================================"
