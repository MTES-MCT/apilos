
export SAL_USE_VCLPLUGIN=gen
export HOME=/app && /app/.apt/usr/bin/soffice --headless --convert-to pdf:writer_pdf_Export --outdir /app/media /app/documents/Avenant-template.docx
export HOME=/app && /app/.apt/usr/bin/libreoffice --headless --convert-to pdf:writer_pdf_Export --outdir /app/media /app/documents/Avenant-template.docx

export PATH=/app/.apt/usr/lib/jvm/java-13-openjdk-amd64/bin:$PATH
export JAVA_HOME=/app/.apt/usr/lib/jvm/java-13-openjdk-amd64
LD_LIBRARY_PATH=/app/.apt/usr/lib/libreoffice/program
unoconv -f pdf /app/documents/Avenant-template.docx
