tempfile=`(mktemp) 2>/dev/null` || tempfile=/tmp/test$$
trap "rm -f $tempfile" 0 $SIG_NONE $SIG_HUP $SIG_INT $SIG_QUIT $SIG_TERM



: "${DIALOG=dialog}"

: "${DIALOG_OK=0}"
: "${DIALOG_CANCEL=1}"
: "${DIALOG_HELP=2}"
: "${DIALOG_EXTRA=3}"
: "${DIALOG_ITEM_HELP=4}"
: "${DIALOG_TIMEOUT=5}"
: "${DIALOG_ESC=255}"

: "${SIG_NONE=0}"
: "${SIG_HUP=1}"
: "${SIG_INT=2}"
: "${SIG_QUIT=3}"
: "${SIG_KILL=9}"
: "${SIG_TERM=15}"



$DIALOG --backtitle "beepy-sdk installer" \
        --help-button \
        --title "beepy-sdk installer" "$@" \
        --checklist "\n\
The default settings below will build the full beepy SDK.\n\n\
Use UP/DOWN ARROWS to move to an option.\n\
Press SPACE to toggle an option on/off. \n\n\
  Which packages should be built?" 20 61 5 \
        "rp2040"    "Build RP2040 firmware" OFF\
        "directfb"  "Build DirectFB"        ON \
        "sdl2"      "Build SDL2"            ON \
        "pygame"    "Build pygame"          ON \
        "bluealsa"  "Audio to Bluetooth headphones" ON \
        2> $tempfile

returncode=$?




case "${returncode:-0}" in
  $DIALOG_OK)
    echo "Result: `cat "$tempfile"`";;
  $DIALOG_CANCEL)
    echo "Cancel pressed.";;
  $DIALOG_HELP)
    echo "Help pressed: `cat "$tempfile"`";;
  $DIALOG_EXTRA)
    echo "Extra button pressed.";;
  $DIALOG_ITEM_HELP)
    echo "Item-help button pressed: `cat "$tempfile"`";;
  $DIALOG_TIMEOUT)
    echo "Timeout expired.";;
  $DIALOG_ESC)
    if test -s "$tempfile" ; then
      cat "$tempfile"
    else
      echo "ESC pressed."
    fi
    ;;
  *)
    echo "Return code was $returncode";;
esac
