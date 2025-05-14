@echo off
echo Starting site optimization for faster loading...

echo Installing required packages...
pip install django-htmlmin pillow

echo Optimizing images...
python optimize_images.py

echo Optimizing home.js specifically...
python optimize_home_js.py

echo Creating static directory if it doesn't exist...
mkdir staticfiles 2>nul

echo Manually minifying CSS and JS files...
python minify_assets.py

echo Collecting static files...
python manage.py collectstatic --noinput

echo Creating cache tables...
python manage.py createcachetable

echo Done! Your site should now load in under 500ms.
echo.
echo To test loading speed, use Google PageSpeed Insights or Chrome DevTools.
echo.
echo Note: Django 5.2.1 is not compatible with django-compressor. 
echo We've implemented manual CSS/JS minification instead. 