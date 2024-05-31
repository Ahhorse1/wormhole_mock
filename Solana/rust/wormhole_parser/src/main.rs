use borsh::{
    BorshDeserialize,
    BorshSerialize,
};

#[derive(Debug, Clone, PartialEq, Eq, BorshSerialize, BorshDeserialize)]
struct A {
   a : i32,
   b:  String,
}

pub type ForeignAddress = [u8; 32];

#[derive(Debug, Default, BorshSerialize, BorshDeserialize)]
pub struct Signature {
    pub index: u8,
    pub r: [u8; 32],
    pub s: [u8; 32],
    pub v: u8,
}

// https://github.com/wormhole-foundation/wormhole/blob/main/solana/bridge/program/src/api/post_vaa.rs#L87

#[derive(Debug, Default, BorshSerialize, BorshDeserialize)]
pub struct PostVAAData {
    // Header part
    pub version: u8,
    pub guardian_set_index: u32,
    // pub signatures: Vec<Signature>,

    // Body part
    pub timestamp: u32,
    pub nonce: u32,
    pub emitter_chain: u16,
    pub emitter_address: ForeignAddress,
    pub sequence: u64,
    pub consistency_level: u8,
    pub payload: Vec<u8>,
}

// https://github.com/wormhole-foundation/wormhole/blob/d87024c9dfdf4a08f714755fe66252e64f5d51a7/solana/bridge/program/src/instructions.rs#L87

// https://github.com/wormhole-foundation/wormhole/blob/dd5388a7483da069082774f7eff68540bf1fe491/solana/bridge/cpi_poster/src/api/post_message.rs

#[repr(u8)]
#[derive(Debug, BorshSerialize, BorshDeserialize)]
pub enum ConsistencyLevel {
    Confirmed,
    Finalized,
}

pub type Address = [u8; 32];
pub type ChainID = u16;

#[derive(BorshDeserialize, BorshSerialize, Default)]
pub struct TransferWrappedData {
    pub nonce: u32,
    pub amount: u64,
    pub fee: u64,
    pub target_address: Address,
    pub target_chain: ChainID,
}

// mhole/blob/d420251f0b801a89625dbbf0123db4ed407009a2/solana/modules/token_bridge/program/src/api/transfer.rs#L295

#[derive(BorshDeserialize, BorshSerialize)]
pub struct PostMessageData {
    /// Unique nonce for this message
    pub nonce: u32,

    /// Message payload
    pub payload: Vec<u8>,

    /// Commitment Level required for an attestation to be produced
    pub consistency_level: ConsistencyLevel,
}

// https://github.com/wormhole-foundation/wormhole/blob/main/solana/bridge/program/src/api/post_message.rs#82

fn hex_string_to_bytes(hex_string: &str) -> Option<Vec<u8>> {
    // Ensure the string has an even number of characters
    if hex_string.len() % 2 != 0 {
        return None;
    }

    // Create a vector to hold the resulting bytes
    let mut bytes = Vec::new();

    // Iterate over the string two characters at a time
    for i in (0..hex_string.len()).step_by(2) {
        let hex_pair = &hex_string[i..i + 2];

        // Parse the hexadecimal pair into a byte
        if let Ok(byte) = u8::from_str_radix(hex_pair, 16) {
            bytes.push(byte);
        } else {
            return None; // Return None if parsing fails
        }
    }

    Some(bytes)
}

// https://github.com/wormhole-foundation/wormhole/blob/aa22a2b950fbbd10221c25a7e19e82e7fd688ed8/solana/bridge/program/src/instructions.rs#L203
// data: (crate::instruction::Instruction::PostVAA 02, vaa)
use std::env;

fn main() {
    // let args: Vec<String> = env::args().collect();

    // if args.len() < 2 {
    //     eprintln!("Missing Arguments");
    //     return;
    // }

    // let hex_string = &args[1];
    // decode_post_vaa(&hex_string);

    let transfer_wrapped = "ee7c0000bdb94b440f000000000000000000000000000000000000000000000065a8f07bd9a8598e1b5b6c0a88f4779dbc0776750200";
    let post_message = "ee7c000085000000010000000000000000000000000000000000000000000000000000000f444bb9bd000000000000000000000000576e2bed8f7b46d34016198911cdf9886f78bea7000200000000000000000000000065a8f07bd9a8598e1b5b6c0a88f4779dbc0776750002000000000000000000000000000000000000000000000000000000000000000001";
    let post_vaa = "0102000000cb36ba6300012b5802000000000000000000000000003ee18b2214aff97000d974cf647e7c347e8fa585438301000000000001850000000100000000000000000000000000000000000000000000000000000000009b019d000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20002fdcab7eb5c1b9bc0af2be72a1f5e9815e321e18f2de99cb4dc107ecc776d542f00010000000000000000000000000000000000000000000000000000000000026b1d";

    decode_transfer_wrapped(&transfer_wrapped);
    decode_post_message(&post_message);
    decode_post_vaa(&post_vaa);

}

fn decode_post_message(hex_string: &str) {
    if let Some(bytes) = hex_string_to_bytes(hex_string) {

        let deserialized_postmsg = PostMessageData::try_from_slice(&bytes).unwrap();

        println!("PostMessageData");
        println!("| Nonce: {}", deserialized_postmsg.nonce);
        println!("| Consistency Level: {:?}", deserialized_postmsg.consistency_level);
        let payload: String = deserialized_postmsg.payload.iter().map(|byte| format!("{:02x}", byte)).collect();
        println!("| Payload: {}", payload);

    } else {
        eprintln!("Invalid hex string!");
    }
}

fn decode_transfer_wrapped(hex_string: &str) {
    if let Some(bytes) = hex_string_to_bytes(hex_string) {

        let deserialized_payload = TransferWrappedData::try_from_slice(&bytes).unwrap();

        println!("TransferWrappedData");
        println!("| Nonce: {}", deserialized_payload.nonce);
        println!("| Amount: {}", deserialized_payload.amount);
        println!("| Fee: {}", deserialized_payload.fee);
        let address_string: String = deserialized_payload.target_address.iter().map(|byte| format!("{:02x}", byte)).collect();
        println!("| Target Address: {}", address_string);
        println!("| Target Chain: {}", deserialized_payload.target_chain);

    } else {
        eprintln!("Invalid hex string!");
    }
}

fn decode_post_vaa(hex_string: &str) {
    if let Some(bytes) = hex_string_to_bytes(hex_string) {

        let deserialized_postvaa = PostVAAData::try_from_slice(&bytes).unwrap();

        println!("PostVAAData");
        println!("| Version: {}", deserialized_postvaa.version);
        println!("| Guardian Set Index: {}", deserialized_postvaa.guardian_set_index);
        println!("| Timestamp: {}", deserialized_postvaa.timestamp);
        println!("| Nonce: {}", deserialized_postvaa.nonce);
        println!("| Emitter Chain: {}", deserialized_postvaa.emitter_chain);
        let emitter_address: String = deserialized_postvaa.emitter_address.iter().map(|byte| format!("{:02x}", byte)).collect();
        println!("| Emitter Address: {}", emitter_address);
        println!("| Sequence: {}", deserialized_postvaa.sequence);
        println!("| Consistency Level: {:?}", deserialized_postvaa.consistency_level);
        let payload: String = deserialized_postvaa.payload.iter().map(|byte| format!("{:02x}", byte)).collect();
        println!("| Payload: {}", payload);

    } else {
        eprintln!("Invalid hex string!");
    }
}