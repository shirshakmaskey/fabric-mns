CHANNEL_NAME="mychannel"
DELAY="3"
TIMEOUT="10"
VERBOSE="false"
COUNTER=1
MAX_RETRY=5
ORG_NAME="$1"
ORDERER_CA=/opt/gopath/src/github.com/hyperledger/fabric/peer/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem


fetchChannelConfig() {
  CHANNEL=$1
  OUTPUT=$2

  echo "Fetching the most recent configuration block for the channel"
  set -x
  peer channel fetch config ./update/config_block.pb -o orderer.example.com:7050 --ordererTLSHostnameOverride orderer.example.com -c $CHANNEL --tls --cafile $ORDERER_CA
  set +x

  echo "Decoding config block to JSON and isolating config to ${OUTPUT}"
  set -x
  configtxlator proto_decode --input ./update/config_block.pb --type common.Block | jq .data.data[0].payload.data.config >"${OUTPUT}"
  set +x
}

createConfigUpdate() {
  CHANNEL=$1
  ORIGINAL=$2
  MODIFIED=$3
  OUTPUT=$4

  set -x
  configtxlator proto_encode --input "${ORIGINAL}" --type common.Config >./update/original_config.pb
  configtxlator proto_encode --input "${MODIFIED}" --type common.Config >./update/modified_config.pb
  configtxlator compute_update --channel_id "${CHANNEL}" --original ./update/original_config.pb --updated ./update/modified_config.pb >./update/config_update.pb
  configtxlator proto_decode --input ./update/config_update.pb --type common.ConfigUpdate >./update/config_update.json
  echo '{"payload":{"header":{"channel_header":{"channel_id":"'$CHANNEL'", "type":2}},"data":{"config_update":'$(cat ./update/config_update.json)'}}}' | jq . >./update/config_update_in_envelope.json
  configtxlator proto_encode --input ./update/config_update_in_envelope.json --type common.Envelope >"${OUTPUT}"
  set +x
}
set -x
mkdir ./update
set +x

# Fetch the config for the channel, writing it to config.json
fetchChannelConfig ${CHANNEL_NAME} ./update/config.json

set -x
jq 'del(.channel_group.groups.Application.groups.'${ORG_NAME}')' ./update/config.json > ./update/modified_config.json
set +x

set -x
createConfigUpdate ${CHANNEL_NAME} ./update/config.json ./update/modified_config.json ./update/org3_update_in_envelope.pb
set +x

exit 0