import base64
import binascii

def toUint8(buffer, index):
    assert len(buffer) >= index + 1, "toUint8 OutOfBounds"

    return int(buffer[index], 16)

def toUint16(buffer, index):
    assert len(buffer) >= index + 2, "toUint16 OutOfBounds"

    return int(''.join(buffer[index:index+2]), 16)

def toUint32(buffer, index):
    assert len(buffer) >= index + 4, "toUint32 OutOfBounds"

    return int(''.join(buffer[index:index+4]), 16)

def toUint64(buffer, index):
    assert len(buffer) >= index + 8, "toUint64 OutOfBounds"

    return int(''.join(buffer[index:index+8]), 16)

def toBytes32(buffer, index):
    assert len(buffer) >= index + 32, "toBytes32 OutOfBounds"

    return ''.join(buffer[index:index+32])

class VAA:
    def __init__(self, vaa_string):
        b64_vaa = base64.b64decode(vaa_string)
        hex_vaa = binascii.hexlify(b64_vaa)
        hex_string = hex_vaa.decode('ascii')
        vaa_list = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)] 
        self.vaa_list = vaa_list

        # Header
        self.num_signers = int(vaa_list[5],16)
        self.version = int(vaa_list[0],16)
        self.guardianSetIndex = toUint32(vaa_list, 1)

        sig_start = 6
        sig_len = 66

        self.body = vaa_list[sig_start + sig_len * self.num_signers:]
        
        # Body
        self.timestamp = toUint32(self.body, 0)
        self.nonce = toUint32(self.body, 4)
        self.emitterChain = toUint16(self.body, 8)
        self.emitterAddress = ''.join(self.body[10:42])
        self.sequence = toUint64(self.body, 42)
        self.consistencyLevel = int(self.body[50], 16)
        self.payload = ''.join(self.body[51:])

        # Payload
        # TODO
    
    def getHeader(self):
        return {'version' : self.version, 
                'guardianSetIndex' : self.guardianSetIndex, 
                'guardianSignatures' : self.num_signers
                }
    
    def getBody(self):
        return {'timestamp' : self.timestamp, 
                'nonce' : self.nonce, 
                'emitterChain' : self.emitterChain,
                'emitterAddress' : self.emitterAddress,
                'sequence' : self.sequence,
                'consistencyLevel' : self.consistencyLevel,
                'payload' : self.payload
                }
    
    def getRawHeader(self):
        return {'version' : self.vaa_list[0], 
                'guardianSetIndex' : ''.join(self.vaa_list[1:5]), 
                'guardianSignatures' : self.vaa_list[5]
                }
    
    def getRawBody(self):
        return {'timestamp' : ''.join(self.body[0:4]), 
                'nonce' : ''.join(self.body[4:8]), 
                'emitterChain' : ''.join(self.body[8:10]),
                'emitterAddress' : self.emitterAddress,
                'sequence' : ''.join(self.body[42:50]),
                'consistencyLevel' : self.body[50],
                'payload' : self.payload
                }

