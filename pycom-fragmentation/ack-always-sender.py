#   +====================================================+ 
#   | RuleID | Dtag | W | FCN ||  PAYLOAD  || padding... |
#   +====================================================+
#

## CONFIGURATION
#select rule ID and DTag for the SCHC packet

##FRAGMENTO TRANSMITIDO
# W -> bit menos significativo de la ventana que se esta enviando
# FCN -> tile index
# Tamaño de tile debe complementar el tamaño del header para que sea multiplo de 8bits

##Tx

# empieza con "blind transmition" de la primera ventana (number 0)
# Luego entra en modo "retransmission phase"
# Inicia Attempts counter en 0
# Inicia "Restransmission timer" (RTx timer)
# Espera por un SCHC ACK

##Retransmission phase

# Si el SCHC ACK indica que se perdieron algunos tiles -> Sender Tx the tiles missng -> incrementar Attempts en 1 -> reset Rtx timer
# Si el SCHC ACK indica que todas las tiles fueron recibidas -> Avanza a la sgte ventana

# Si la actual ventana es la ultima pero el ACK indica que se recibieron mas tiles que las enviadas
#   -> sender envia un SCHC Sender-Abort y reetorna un ERROR
# Si la actual ventana es la ultima pero el ACK indica que el Integrity Check fallo
#   -> sender envia un SCHC Sender-Abort y retorna con ERROR
# Si la actual ventana es la ultima y el ACK indica que el Integrity Check es correcto
#   -> Sender retorna con EXITO

# Si el RTx Timer expira 
#   -> Si Attempts < MAX_ACK_REQUESTS -> Sender envia un SCHC ACK REQ e incremepta Attempts en 1
#   -> Si Attempts >= MAX_ACK_REQUESTS -> Sender envia SCHC Sender-Abort

##En cualquier momento

# Si se recibe un SCHC Receiver-Abort -> retorna con ERROR
# Si se recibe un SCHC ACK con diferente valor de W que el de la ventana enviada -> SCHC ACK se descarta

##NOTES
# El fragmento de la ultima tile debe ser un ALL-1 SCHC fragment.
# Each SCHC fragment debe contener 1 tile en su payload
# Tiles index 0 y ultima tile deben ser de de minimo 1 byte

