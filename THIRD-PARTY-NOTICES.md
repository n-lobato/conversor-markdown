# Componentes de terceiros

O Conversor Markdown é distribuído sob a licença GNU AGPL v3 (arquivo `LICENSE`).
Ele usa os componentes abaixo, cada um com a sua própria licença. Os textos das
licenças acompanham a versão portátil, na pasta `LICENCAS`.

## Bibliotecas Python principais

| Componente | Uso no conversor | Licença |
| --- | --- | --- |
| [PyMuPDF](https://github.com/pymupdf/PyMuPDF) (inclui PyMuPDF4LLM e PyMuPDF Layout) | Leitura de PDF e conversão para Markdown | AGPL-3.0 ou licença comercial Artifex |
| [mammoth](https://github.com/mwilliamson/python-mammoth) | Leitura de Word (.docx) | BSD-2-Clause |
| [markdownify](https://github.com/matthewwithanm/python-markdownify) | HTML para Markdown | MIT |
| [python-pptx](https://github.com/scanny/python-pptx) | Leitura de PowerPoint (.pptx) | MIT |
| [openpyxl](https://foss.heptapod.net/openpyxl/openpyxl) | Leitura de Excel (.xlsx) | MIT |
| [xlrd](https://github.com/python-excel/xlrd) | Leitura de Excel antigo (.xls) | BSD |
| [pytesseract](https://github.com/madmaze/pytesseract) | Ponte com o Tesseract | Apache-2.0 |
| [Pillow](https://github.com/python-pillow/Pillow) | Imagens | MIT-CMU |
| [tkinterdnd2](https://github.com/Eliav2/tkinterdnd2) (inclui tkdnd) | Arrastar e soltar | MIT |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) | Análise de layout do PyMuPDF | MIT |

A lista completa, com versões, é gerada automaticamente no build
(`LICENCAS/python/_INDICE.md` na versão portátil).

## Python e Tcl/Tk

O executável inclui o interpretador [Python](https://www.python.org) (licença PSF)
e o [Tcl/Tk](https://www.tcl-lang.org) (licença BSD do Tcl/Tk), empacotados com
[PyInstaller](https://pyinstaller.org), cuja licença permite distribuir programas
gerados por ele.

## Tesseract OCR

O OCR usa o [Tesseract](https://github.com/tesseract-ocr/tesseract) (Apache-2.0),
com os modelos de idioma `por` e `eng` do repositório
[tessdata](https://github.com/tesseract-ocr/tessdata) (Apache-2.0).
Os binários para Windows vêm da compilação da
[Biblioteca da Universidade de Mannheim](https://github.com/UB-Mannheim/tesseract),
feita sobre pacotes do [MSYS2](https://packages.msys2.org), onde está o código-fonte
de cada biblioteca abaixo.

A versão portátil leva apenas as DLLs que o `tesseract.exe` realmente usa:

| Biblioteca | Arquivo | Licença |
| --- | --- | --- |
| Tesseract | libtesseract-5.dll | Apache-2.0 |
| Leptonica | libleptonica-6.dll | BSD-2-Clause |
| libarchive | libarchive-13.dll | BSD-2-Clause |
| BLAKE2 | libb2-1.dll | CC0-1.0, OpenSSL ou Apache-2.0 |
| bzip2 | libbz2-1.dll | bzip2 (estilo BSD) |
| OpenSSL | libcrypto-3-x64.dll | Apache-2.0 |
| libdeflate | libdeflate.dll | MIT |
| Expat | libexpat-1.dll | MIT |
| GCC runtime | libgcc_s_seh-1.dll, libstdc++-6.dll | GPL-3.0 com GCC Runtime Library Exception |
| GIFLIB | libgif-7.dll | MIT |
| GNU libiconv | libiconv-2.dll | LGPL-2.1-or-later |
| JBIG-KIT | libjbig-0.dll | GPL-2.0-or-later |
| libjpeg-turbo | libjpeg-8.dll | IJG, BSD-3-Clause e zlib |
| LERC | libLerc.dll | Apache-2.0 |
| LZ4 | liblz4.dll | BSD-2-Clause |
| XZ Utils | liblzma-5.dll | 0BSD / domínio público |
| OpenJPEG | libopenjp2-7.dll | BSD-2-Clause |
| libpng | libpng16-16.dll | libpng |
| libwebp | libwebp-7.dll, libwebpmux-3.dll, libsharpyuv-0.dll | BSD-3-Clause |
| libtiff | libtiff-6.dll | libtiff (estilo BSD) |
| mingw-w64 winpthreads | libwinpthread-1.dll | MIT e ZPL-2.1 |
| Zstandard | libzstd.dll | BSD-3-Clause |
| zlib | zlib1.dll | zlib |

As bibliotecas sob GPL/LGPL são distribuídas sem modificação, como arquivos DLL
separados, e o código-fonte delas está disponível nos endereços acima.
