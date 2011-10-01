#!/bin/bash
# ./gen_words.sh '#ffff66' '#003399'
set -e
DIR=$(dirname $0)
DEST=${DIR}/../static/img/words
usage() 
{
    cat << EOF
Generates images from a file in ${DIR} named words.txt and 
copies them to ${DEST}

WILL REMOVE FILES IN ${DEST} IF THEY EXIST

Usage:   $0 <fill color> <outline color> <file>
Example: $0 '#ffff66' '#003399' words.txt

EOF

}

if [[ $# -ne 3 ]]; then
    usage
    exit
fi

if [[ ! -f $3 ]]; then
    echo "Can't open $3"
    usage
    exit
fi

mkdir -p $DEST
rm -f ${DEST}/*

perl -ane '$a{$F[0]}++; END { for (keys(%a)) {print "$_\x0";} }' $3 | xargs -0 -n1 -i convert -size 500x68 xc:transparent -font ResPublica-Regular -pointsize 52 -fill $1 -strokewidth 2 -stroke $2 -draw 'text 1,55 "{}"' -channel RGBA ${DEST}/{}.png

find ${DEST} -name "*.png" -print0 | xargs -0 -n1 -i convert "{}" -trim "{}"
