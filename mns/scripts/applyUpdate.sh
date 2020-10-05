CHANNEL_NAME="mychannel"
DELAY="3"
TIMEOUT="10"
VERBOSE="false"
COUNTER=1
MAX_RETRY=5
ORDERER_CA=/opt/gopath/src/github.com/hyperledger/fabric/peer/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

echo
echo "========= Submitting transaction from a different peer which also signs it ========= "
echo
setGlobals 3
set -x
peer channel update -f ./update/org3_update_in_envelope.pb -c ${CHANNEL_NAME} -o orderer.example.com:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${ORDERER_CA}
set +x

set -x
rm -rf ./update
set +x

exit 0