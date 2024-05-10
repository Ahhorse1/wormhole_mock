from collections import defaultdict
from SafeERC20 import SafeERC20

MAX_UINT64 = (1 << 64) - 1

class Contract:
    def __init__(self):
        self.wrappedAssets = defaultdict(bool)
        self.chainID = 2
        self.address = '0x3ee18B2214AFF97000D974cf647E7C347E8fa585'.lower()
        self.msg_sender = '0x5bd1b6b7ec91eb8b21e9e7349c6d4bebf0078435'.lower()
        self.msg_value = 0
        self.finality = 0

        self._state = defaultdict()
        self._state['outstandingBridged'] = defaultdict(int)

        self.ERC20_Tokens = defaultdict(SafeERC20)

        SmarDex = SafeERC20()
        SmarDex.constructor('SmarDex', 'SDEX')
        SmarDex.set_balance('0x5Bd1b6b7EC91eb8B21e9e7349c6d4BebF0078435'.lower(), 38012880422754149229822)
        SmarDex.set_balance('0x3ee18B2214AFF97000D974cf647E7C347E8fa585'.lower(), 1296037968379177100000000000)
        SmarDex.set_allowances('0x5Bd1b6b7EC91eb8B21e9e7349c6d4BebF0078435'.lower(), '0x3ee18B2214AFF97000D974cf647E7C347E8fa585'.lower(), 38012880422754149229822)
        SmarDex.set_msgSender('0x3ee18b2214aff97000d974cf647e7c347e8fa585'.lower())

        self.ERC20_Tokens['0x5DE8ab7E27f6E7A1fFf3E5B337584Aa43961BEeF'.lower()] = SmarDex
    
    # https://etherscan.io/tx/0x00718350702d0f67f0d3090bdf2f8564cfa8927f749dffcf87688b348223eeae
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
        decimals = self.ERC20_Tokens[token.lower()].decimals()
        amount = self.deNormalizeAmount(self.normalizeAmount(amount, decimals), decimals)

        if tokenChain == self.chainID:

            # print('Querying Balance Before')
            # (,bytes memory queriedBalanceBefore) = token.staticcall(abi.encodeWithSelector(IERC20.balanceOf.selector, address(this)));
            # uint256 balanceBefore = abi.decode(queriedBalanceBefore, (uint256));
            balanceBefore = self.ERC20_Tokens[token.lower()].balanceOf(self.address)

            # print('Transferring Tokens') # TODO
            # SafeERC20.safeTransferFrom(IERC20(token), msg.sender, address(this), amount);
            self.ERC20_Tokens[token.lower()].safeTransferFrom(token, self.msg_sender, self.address, amount)

            # print('Querying Balance After')
            # (,bytes memory queriedBalanceAfter) = token.staticcall(abi.encodeWithSelector(IERC20.balanceOf.selector, address(this)));
            # uint256 balanceAfter = abi.decode(queriedBalanceAfter, (uint256));
            balanceAfter = self.ERC20_Tokens[token.lower()].balanceOf(self.address)

            amount = balanceAfter - balanceBefore
        else:
            # print('Transfering Tokens')
            # SafeERC20.safeTransferFrom(IERC20(token), msg.sender, address(this), amount);
            self.ERC20_Tokens[token.lower()].safeTransferFrom(token, self.msg_sender, self.address, amount)

            # print('Burning Tokens')
            # TokenImplementation(token).burn(address(this), amount); # TODO: burn to address x
            self.ERC20_Tokens[token.lower()]._burn(self.address, amount)

            # tokens are wrapped and their collateral is being withdrew from the other side so these tokens are no longer backed by anything

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
        outstandingAmount = self.outstandingBridged(token)
        assert outstandingAmount + normalizedAmount <= MAX_UINT64, "Transfer Exceeds Max Outstanding Bridged Token Amount"
        self.setOutstandingBridge(token, outstandingAmount + normalizedAmount)
        return None

    def outstandingBridged(self, token):
        return self._state['outstandingBridged'][token]

    def setOutstandingBridge(self, token, amount):
        self._state['outstandingBridged'][token] = amount

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