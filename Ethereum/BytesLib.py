class BytesLib:
    def toUint8(encodedVM, index):
        assert len(encodedVM) >= index + 2, "toUint8 OutOfBounds"

        return int(encodedVM[index:index+2], 16)

    def toUint16(encodedVM, index):
        assert len(encodedVM) >= index + 4, "toUint32 OutOfBounds"

        return int(encodedVM[index, index+4], 16)
    
    def toUint32(encodedVM, index):
        assert len(encodedVM) >= index + 8, "toUint32 OutOfBounds"

        return int(encodedVM[index, index+8], 16)
    
    def toUint64(encodedVM, index):
        assert len(encodedVM) >= index + 16, "toUint32 OutOfBounds"

        return int(encodedVM[index, index+16], 16)

    def toBytes32(encodedVM, index):
        assert len(encodedVM) >= index + 64, "toBytes32 OutOfBounds"

        return encodedVM[index: index+64]