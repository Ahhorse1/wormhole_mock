from collections import defaultdict
from SafeERC20 import SafeERC20

class Contract:
    def __init__(self):
        self.wrappedAssets = defaultdict(bool)
        self
        self.chainID = 2
        self.decimal = 18
        self.balance_before = 1296037968379177100000000000
        self.balance_after = 1296038968379177100000000000
        self.msg_value = 0
        self.finality = 1
    
    def transferTokens(self, token, amount, recipientChain, recipient, arbiterFee, nonce) -> int:
        transferResult = self._transferTokens(token, amount, arbiterFee)
        sequence = self.logTransfer(transferResult['tokenChain'], transferResult['tokenAddress'], transferResult['normalizedAmount'], recipientChain, recipient, transferResult['normalizedArbiterFee'], transferResult['wormholeFee'], nonce);
        return sequence

    def _transferTokens(self, token, amount, arbiterFee) -> dict:
        tokenChain = 0
        tokenAddress = 0x0
        if self.isWrappedAsset(token):
            print('Not Wrapped Asset') #  TODO: do a mapping
        else:
            tokenChain = self.chainID
            tokenAddress = token[2:].rjust(64, '0')

        print('Querying Token\'s decimals()')
        # (,bytes memory queriedDecimals) = token.staticcall(abi.encodeWithSignature("decimals()"));
        # uint8 decimals = abi.decode(queriedDecimals, (uint8));
        decimals = self.decimal
        amount = self.deNormalizeAmount(self.normalizeAmount(amount, decimals), decimals)

        if tokenChain == self.chainID:

            print('Querying Balance Before')
            # (,bytes memory queriedBalanceBefore) = token.staticcall(abi.encodeWithSelector(IERC20.balanceOf.selector, address(this)));
            # uint256 balanceBefore = abi.decode(queriedBalanceBefore, (uint256));
            balanceBefore = self.balance_before

            print('Transferring Tokens') # TODO
            # SafeERC20.safeTransferFrom(IERC20(token), msg.sender, address(this), amount);

            print('Querying Balance After')
            # (,bytes memory queriedBalanceAfter) = token.staticcall(abi.encodeWithSelector(IERC20.balanceOf.selector, address(this)));
            # uint256 balanceAfter = abi.decode(queriedBalanceAfter, (uint256));
            balanceAfter = self.balance_after

            amount = balanceAfter - balanceBefore
        else:
            print('Transfering Tokens')
            # SafeERC20.safeTransferFrom(IERC20(token), msg.sender, address(this), amount);

            print('Burning Tokens')
            # TokenImplementation(token).burn(address(this), amount); # TODO: burn to address x
        
        normalizedAmount = self.normalizeAmount(amount, decimals)
        normalizedArbiterFee = self.normalizeAmount(arbiterFee, decimals)

        if tokenChain == self.chainID:
            self.bridgeOut(token, normalizedAmount)

        transferResult = {'tokenChain': tokenChain, 'tokenAddress': tokenAddress, 'normalizedAmount': normalizedAmount, 'normalizedArbiterFee': normalizedArbiterFee, 'wormholeFee': self.msg_value}
        
        return transferResult
        

    def isWrappedAsset(self, token):
        return self.wrappedAssets[token]

    def normalizeAmount(self, amount: int, decimals: int) -> int:
        if decimals > 8:
            amount = amount // 10 ** (decimals - 8)
        
        return amount

    def deNormalizeAmount(self, amount: int, decimals: int) -> int:
        if decimals > 8:
            amount *= 10 ** (decimals - 8)
        
        return amount

    def bridgeOut(self, token, normalizedAmount):
        # outstandingAmount = outstandingBridged(token)
        # assert outstandingAmount + normalizedAmount <= MAX_UINT64, "Transfer Exceeds Max Outstanding Bridged Token Amount"
        # setOutstandingBridge(token, outstandingAmount + normalizedAmount)
        return None

    def outstandingBridged(self, token):
        return None

    def setOutstandingBridge(self, token, amount):
        return None

    def logTransfer(self, tokenChain, tokenAddress, amount, recipientChain, recipient, fee, callValue, nonce):
        transfer = {'payloadID': 1, 'amount': amount, 'tokenAddress': tokenAddress, 'tokenChain': tokenChain, 'to': recipient, 'toChain': recipientChain, 'fee': fee}

        print(f'Nonce: {nonce}')

        encodedResult = self.encodedTransfer(transfer)

        print(f'Payload: {encodedResult}')

        print(f'Consistency Level: {self.finality}')

        return None

    def encodedTransfer(self, transfer):
        payloadID = transfer['payloadID']
        string = hex(payloadID)[2:]
        encode = string.rjust(2, '0')

        amount = transfer['amount']
        string = hex(amount)[2:]
        encode += string.rjust(64, '0')

        tokenAddress = transfer['tokenAddress']
        encode += tokenAddress.rjust(64, '0')

        tokenChain = transfer['tokenChain']
        string = hex(tokenChain)[2:]
        encode += string.rjust(4, '0')

        toAddress = transfer['to']
        string = toAddress[2:]
        encode += string.rjust(64, '0')

        toChain = transfer['toChain']
        string = hex(toChain)[2:]
        encode += string.rjust(4, '0')

        fee = transfer['fee']
        string = hex(fee)[2:]
        encode += string.rjust(64, '0')

        return encode
    
# struct VM {
# 	uint8 version;
# 	uint32 timestamp;
# 	uint32 nonce;
# 	uint16 emitterChainId;
# 	bytes32 emitterAddress;
# 	uint64 sequence;
# 	uint8 consistencyLevel;
# 	bytes payload;

# 	uint32 guardianSetIndex;
# 	Signature[] signatures;

# 	bytes32 hash;
# }

