> scalingo --region osc-fr1 --app apilos-staging run bash

export SAL_USE_VCLPLUGIN=gen
export HOME=/app && /app/.apt/usr/bin/soffice --headless --convert-to pdf:writer_pdf_Export --outdir /app/media /app/documents/Avenant-template.docx
export HOME=/app && /app/.apt/usr/bin/libreoffice --headless --convert-to pdf:writer_pdf_Export --outdir /app/media /app/documents/Avenant-template.docx

LD_LIBRARY_PATH=/app/.apt/usr/lib/libreoffice/program
unoconv -f pdf /app/documents/Avenant-template.docx

### Test Scalingo staging

mkdir -p /app/libreoffice-config
/app/.apt/usr/bin/libreoffice --headless -env:UserInstallation=file:///app/libreoffice-config -env:SAL_USE_VCLPLUGIN=gen --convert-to pdf:writer_pdf_Export --outdir /app/media /app/documents/Avenant-template.docx

### Test en local

mkdir -p /tmp/libreoffice-config
libreoffice --headless -env:UserInstallation=file:///tmp/libreoffice-config --convert-to pdf:writer_pdf_Export --outdir /tmp ./documents/Avenant-template.docx

unoconvert --convert-to pdf:writer_pdf_Export ./documents/Avenant-template.docx /tmp/Avenant-template.pdf

### APT list

libreoffice-core-nogui
libreoffice-java-common
libreoffice-script-provider-python
uno-libs-private
python3-uno
unoconv

### Python requirements

uno
unoserver
unotools


### Solution en passant par l'appimage

Doc: https://github.com/BlueTeaLondon/heroku-buildpack-libreoffice-for-heroku-18/blob/master/bin/compile

Ajout du buildpack: https://github.com/BlueTeaLondon/heroku-buildpack-libreoffice-for-heroku-18.git

Commande:
/app/vendor/libreoffice/opt/libreoffice7.3/program/soffice --headless --convert-to pdf:writer_pdf_Export --outdir /app/media /app/documents/Avenant-template.docx
