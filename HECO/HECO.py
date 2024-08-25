from Crypto.Hash import keccak
from eth_abi import packed

def keccak256(data):
    hash_object = keccak.new(digest_bits=256)
    hash_object.update(data)
    return hash_object.hexdigest()

def check_hash(to, value, proof, actual_taskHash):
    types = ['address','uint256','string']
    values = [to, value, proof]
    encoded_data = packed.encode_packed(types, values)
    taskHash = keccak256(encoded_data)
    return (taskHash == actual_taskHash)

def generate_hash(to, value, proof):
    types = ['address','uint256','string']
    values = [to, value, proof]
    encoded_data = packed.encode_packed(types, values)
    taskHash = keccak256(encoded_data)
    return taskHash