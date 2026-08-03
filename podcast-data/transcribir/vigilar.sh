#!/bin/bash
PID=19741
while kill -0 "$PID" 2>/dev/null; do
    sleep 120
done
if tail -5 transcribir_nohup.log | grep -q "^\[.*\] listo\."; then
    RESUMEN=$(tail -1 transcribir_nohup.log)
    osascript -e "display notification \"$RESUMEN\" with title \"Punzadas Sonoras\" subtitle \"Transcripción terminada\" sound name \"Glass\""
    echo "TERMINADO OK: $RESUMEN"
else
    RESUMEN=$(tail -8 transcribir_nohup.log | tr '\n' ' ')
    osascript -e "display notification \"El proceso se paró sin terminar\" with title \"Punzadas Sonoras\" subtitle \"Revisa transcribir_nohup.log\" sound name \"Basso\""
    echo "PROCESO MUERTO SIN TERMINAR: $RESUMEN"
fi
