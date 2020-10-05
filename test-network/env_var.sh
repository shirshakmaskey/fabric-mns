eval export CORE_PEER_TLS_ENABLED=true
eval export CORE_PEER_LOCALMSPID="Org1MSP"
eval export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
eval export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
eval export CORE_PEER_ADDRESS=localhost:7051
