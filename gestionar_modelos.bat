@echo off
:menu
cls
echo ============================================
echo     GESTION DE MODELOS - Calculadora KIA
echo ============================================
echo.
echo  1. Listar modelos Full Service
echo  2. Listar modelos Unlimited
echo  3. Listar modelos 2 Servicios (DS)
echo  4. Eliminar modelo Full Service
echo  5. Eliminar modelo Unlimited
echo  6. Eliminar modelo 2 Servicios (DS)
echo  7. Agregar modelo Full Service
echo  8. Agregar modelo Unlimited
echo  9. Agregar modelo 2 Servicios (DS)
echo  0. Salir
echo.
set /p opcion="Elige una opcion (0-9): "

if "%opcion%"=="1" goto list_fs
if "%opcion%"=="2" goto list_ul
if "%opcion%"=="3" goto list_ds
if "%opcion%"=="4" goto remove_fs
if "%opcion%"=="5" goto remove_ul
if "%opcion%"=="6" goto remove_ds
if "%opcion%"=="7" goto add_fs
if "%opcion%"=="8" goto add_ul
if "%opcion%"=="9" goto add_ds
if "%opcion%"=="0" exit
goto menu

:list_fs
cls
python manage_models.py list-fs
pause
goto menu

:list_ul
cls
python manage_models.py list-ul
pause
goto menu

:list_ds
cls
python manage_models.py list-ds
pause
goto menu

:remove_fs
cls
echo Ejemplo de clave: PICANTO JA|1.0|MT|5K|
echo (Usa la opcion 1 para ver las claves exactas)
echo.
set /p clave="Clave a eliminar: "
python manage_models.py remove-fs "%clave%"
pause
goto menu

:remove_ul
cls
echo Ejemplo de clave: PICANTO JA|1.0|MT|5K||20K - 50K
echo (Deja el rango vacio para eliminar todos los rangos del modelo)
echo (Usa la opcion 2 para ver las claves exactas)
echo.
set /p clave="Clave a eliminar: "
python manage_models.py remove-ul "%clave%"
pause
goto menu

:remove_ds
cls
echo Ejemplo de clave: Picanto (JA)|1.0|MT|10K|Gasolina
echo (Usa la opcion 3 para ver las claves exactas)
echo.
set /p clave="Clave a eliminar: "
python manage_models.py remove-ds "%clave%"
pause
goto menu

:add_fs
cls
echo Formato de clave: MODELO|motor|trans|freq|combustible
echo Ejemplo:          NUEVO MODELO|1.6|DCT|10K|
echo (Para EVs sin motor ni trans: EV NUEVO|||15K|)
echo.
set /p clave="Clave del nuevo modelo: "
set /p nombre="Nombre para mostrar en la calculadora: "
python manage_models.py add-fs "%clave%" "%nombre%"
pause
goto menu

:add_ul
cls
echo Formato de clave: MODELO|motor|trans|freq|combustible|rango
echo Ejemplo:          NUEVO MODELO|1.6|DCT|10K||20K - 50K
echo.
set /p clave="Clave del nuevo modelo con rango: "
python manage_models.py add-ul "%clave%"
pause
goto menu

:add_ds
cls
echo Formato de clave: Modelo|motor|trans|freq|combustible
echo Ejemplo:          Nuevo Modelo|1.6|DCT|10K|Gasolina
echo.
set /p clave="Clave del nuevo modelo: "
set /p pares="Pares de KM separados por coma (ej: 5K-10K, 10K-20K, 20K-30K): "
python manage_models.py add-ds "%clave%" %pares%
pause
goto menu
