@echo off


start /wait cmd /k "%cd%\venv\Scripts\activate && pip --pre install torch==2.1.0.dev20230713+cpu torchvision==0.16.0.dev20230713+cpu -f https://download.pytorch.org/whl/nightly/cpu/torch_nightly.html && exit"

echo torch 2.1.0 dev installation completed.

powershell -executionpolicy bypass .\torch-install.ps1


echo eval_frame.py modification completed. press any key to exit
pause
