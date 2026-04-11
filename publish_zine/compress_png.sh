#pngcrush -v -brute -reduce -ow ./background_raw.png

optipng   -v -full   -zw 32k   -zc1-9 -zm1-9 -zs0-3 -f0-5   ./background_raw.png
