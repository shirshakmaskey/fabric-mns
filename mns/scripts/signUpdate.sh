# signConfigtxAsPeerOrg <org> <configtx.pb>
# Set the peerOrg admin of an org and signing the config update
signConfigtxAsPeerOrg() {
  TX=$1
  set -x
  peer channel signconfigtx -f "${TX}"
  set +x
}

echo "=========Signing config transaction by ORGA========="
echo
set -x
signConfigtxAsPeerOrg ./update/org3_update_in_envelope.pb
set +x
echo

exit 0