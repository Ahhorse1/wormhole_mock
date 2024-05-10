CURRENT_CHAIN_ID = 2
DECIMAL = 18
BEFORE_BALANCE_OF = 1296037968379177100000000000
AFTER_BALANCE_OF =  1296038968379177100000000000
MAX_UINT64 = (1 << 64) - 1
MSG_VALUE = 0
FINALITY = 1

# TODO: how do I know what tokens are accepted
def transferTokens(token, amount, recipientChain, recipient, arbiterFee, nonce):
    transferResult = _transferTokens(token, amount, arbiterFee)
    sequence = logTransfer(transferResult['tokenChain'], transferResult['tokenAddress'], transferResult['normalizedAmount'], recipientChain, recipient, transferResult['normalizedArbiterFee'], transferResult['wormholeFee'], nonce);

def _transferTokens(token, amount, arbiterFee):
    tokenChain = 0
    tokenAddress = 0x0
    if isWrappedAsset(token):
        print('Not Wrapped Asset') #  TODO: do a mapping
    else:
        tokenChain = CURRENT_CHAIN_ID
        tokenAddress = token[2:].rjust(64, '0')

    print('Querying Token\'s decimals()')
    # (,bytes memory queriedDecimals) = token.staticcall(abi.encodeWithSignature("decimals()"));
    # uint8 decimals = abi.decode(queriedDecimals, (uint8));
    decimals = DECIMAL
    amount = deNormalizeAmount(normalizeAmount(amount, decimals), decimals)

    if tokenChain == CURRENT_CHAIN_ID:

        print('Querying Balance Before')
        # (,bytes memory queriedBalanceBefore) = token.staticcall(abi.encodeWithSelector(IERC20.balanceOf.selector, address(this)));
        # uint256 balanceBefore = abi.decode(queriedBalanceBefore, (uint256));
        balanceBefore = BEFORE_BALANCE_OF

        print('Transferring Tokens')
        # SafeERC20.safeTransferFrom(IERC20(token), msg.sender, address(this), amount);

        print('Querying Balance After')
        # (,bytes memory queriedBalanceAfter) = token.staticcall(abi.encodeWithSelector(IERC20.balanceOf.selector, address(this)));
        # uint256 balanceAfter = abi.decode(queriedBalanceAfter, (uint256));
        balanceAfter = AFTER_BALANCE_OF

        amount = balanceAfter - balanceBefore
    else:
        print('Transfering Tokens')
        # SafeERC20.safeTransferFrom(IERC20(token), msg.sender, address(this), amount);

        print('Burning Tokens')
        # TokenImplementation(token).burn(address(this), amount); # TODO: burn to address x
    
    normalizedAmount = normalizeAmount(amount, decimals)
    normalizedArbiterFee = normalizeAmount(arbiterFee, decimals)

    if tokenChain == CURRENT_CHAIN_ID:
        bridgeOut(token, normalizedAmount)

    transferResult = {'tokenChain': tokenChain, 'tokenAddress': tokenAddress, 'normalizedAmount': normalizedAmount, 'normalizedArbiterFee': normalizedArbiterFee, 'wormholeFee': MSG_VALUE}
    
    return transferResult
    

def isWrappedAsset(token):
    return False

def normalizeAmount(amount, decimals):
    if decimals > 8:
        amount = amount // 10 ** (decimals - 8)
    
    return amount

def deNormalizeAmount(amount, decimals):
    if decimals > 8:
        amount *= 10 ** (decimals - 8)
    
    return amount

def bridgeOut(token, normalizedAmount):
    # outstandingAmount = outstandingBridged(token)
    # assert outstandingAmount + normalizedAmount <= MAX_UINT64, "Transfer Exceeds Max Outstanding Bridged Token Amount"
    # setOutstandingBridge(token, outstandingAmount + normalizedAmount)
    return None

def outstandingBridged(token):
    return None

def setOutstandingBridge(token, amount):
    return None

def logTransfer(tokenChain, tokenAddress, amount, recipientChain, recipient, fee, callValue, nonce):
    transfer = {'payloadID': 1, 'amount': amount, 'tokenAddress': tokenAddress, 'tokenChain': tokenChain, 'to': recipient, 'toChain': recipientChain, 'fee': fee}

    print(f'Nonce: {nonce}')

    encodedResult = encodedTransfer(transfer)

    print(f'Payload: {encodedResult}')

    print(f'Consistency Level: {FINALITY}')

    return None

def encodedTransfer(transfer):
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

transferTokens('0x5DE8ab7E27f6E7A1fFf3E5B337584Aa43961BEEF', 1000000000000000000000, 4, '0x0000000000000000000000005bd1b6b7ec91eb8b21e9e7349c6d4bebf0078435', 0, 20)
