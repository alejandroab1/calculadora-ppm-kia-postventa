@echo off
echo Instalando dependencias...
pip install openpyxl
echo.
echo Actualizando precios...
python update_prices.py
pause
