ARGS1="$1"
ARGS2="$2"
ARGS3="$3"
ARGS4="$4"
ARGS5="$5"
ARGS6="$6"
ARGS7="$7"
ARGS8="$8"
ARGS9="$9"
ARGS10="${10}"
ARGS11="${11}"

ORGA="${12}"
ORGB="${13}"
ORGC="${14}"
ORGD="${15}"
ORGE="${16}"
CHANNEL_NAME="mychannel"
CC_SRC_LANGUAGE="golang"
VERSION="1"
SEQUENCE="1"
DELAY="3"
MAX_RETRY="5"
VERBOSE="false"
CC_SRC_LANGUAGE=`echo "$CC_SRC_LANGUAGE" | tr [:upper:] [:lower:]`

export FABRIC_CFG_PATH=$PWD/../config/

# import utils
. scripts/envVar.sh

chaincodeInvoke() {
  parsePeerConnectionParameters $@
  res=$?
  verifyResult $res "Invoke transaction failed on channel '$CHANNEL_NAME' due to uneven number of peer and org parameters "

  # while 'peer chaincode' command can get the orderer endpoint from the
  # peer (if join was successful), let's supply it directly as we know
  # it using the "-o" option
  if [ -z "$CORE_PEER_TLS_ENABLED" -o "$CORE_PEER_TLS_ENABLED" = "false" ]; then
    set -x
    peer chaincode invoke -o localhost:7050 -C $CHANNEL_NAME -n basic $PEER_CONN_PARMS  -c '{"function":"UpdateAsset","Args":['${ARGS1}','${ARGS2}','${ARGS3}','${ARGS4}','${ARGS5}','${ARGS6}','${ARGS7}','${ARGS8}','${ARGS9}','${ARGS10}','${ARGS11}']}' >&log.txt
    res=$?
    set +x
  else
    set -x
    peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls $CORE_PEER_TLS_ENABLED --cafile $ORDERER_CA -C $CHANNEL_NAME -n basic $PEER_CONN_PARMS -c '{"function":"UpdateAsset","Args":["T-6","659","Wed Jul 24 15:58:22 EDT 2013","29","0.0","84.0","0","39.980572","-82.953895","NULL","NULL"]}' >&log.txt
    res=$?
    set +x
	fi
  cat log.txt
  verifyResult $res "Invoke execution on $PEERS failed "
  echo "===================== Invoke transaction successful on $PEERS on channel '$CHANNEL_NAME' ===================== "
  echo
}
chaincodeInvoke $ORGA $ORGB $ORGC $ORGD $ORGE