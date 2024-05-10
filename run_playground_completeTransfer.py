def completeTransfer(encodedVM):
    _completeTransfer(encodedVM, False)

def _completeTransfer(encodedVM, unwrapWETH):
    vm, valid, reason = parseAndVerifyVM(encodedVM)

    assert valid, reason
    assert verifyBridge(vm), "invalid emitter"

def parseAndVerifyVM(encodedVM):
    vm = parseVM(encodedVM)
    (valid, reason) = verifyVMInternal(vm, False)

def parseVM(encodedVM):
    vm = {}
    index = 0

    vm['version'] = toUint8(encodedVM, index)
    index += 2

    vm['guardianSetIndex'] = toUint32(encodedVM, index)
    index += 8

    signersLen = toUint8(encodedVM, index)
    index += 2

    signatures = []
    for i in range(signersLen):
        guardianIndex = toUint8(encodedVM, index)
        index += 2

        r = toBytes32(encodedVM, index)
        index += 64
        s = toBytes32(encodedVM, index)
        index += 64
        v = toBytes32(encodedVM, index)
        index += 64

        signatures.append(guardianIndex, r, s, v)
    
    body = encodedVM[index:]
    

def toUint8(encodedVM, index):
    assert len(encodedVM) >= index + 2, "toUint8 OutOfBounds"

    return int(encodedVM[index:index+2], 16)

def toUint32(encodedVM, index):
    assert len(encodedVM) >= index + 8, "toUint32 OutOfBounds"

    return int(encodedVM[index, index+8], 16)

def toBytes32(encodedVM, index):
    assert len(encodedVM) >= index + 64, "toBytes32 OutOfBounds"

    return encodedVM[index: index+64]
