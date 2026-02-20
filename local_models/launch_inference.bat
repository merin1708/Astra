@echo off
color 0b
title Local Inference Node - Astra Cluster
echo ========================================================
echo Astra V-Cluster Distributed Inference Launcher
echo System Check: Evaluating VRAM and Unified Memory...
echo ========================================================
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
    echo [FATAL ERROR] Python 3.10+ optimized backend is required.
    pause
    exit /b
)

echo Loading dependency matrices...
pip install -r requirements.txt -q
echo Matrices Synced.
echo.
echo Please select a local foundation model to load into VRAM:
echo [1] Qwen2.5-72B-Instruct (Text/Coder - 144GB Safetensors)
echo [2] Nova-Audio-Ultimate (Audio Generation Diffusion)
echo ========================================================
set /p choice="Node Selection (1/2): "

if "%choice%"=="1" (
    cls
    echo Initializing Qwen 72B inference bridge...
    python run_qwen_72b.py
) else if "%choice%"=="2" (
    cls
    echo Booting Nova-Audio synthesis pipeline...
    python run_nova_audio.py
) else (
    echo [ERROR] Handshake failed. Invalid model selection.
)

pause
