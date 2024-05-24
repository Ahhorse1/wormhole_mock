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
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        eprintln!("Missing Arguments");
        return;
    }

    let hex_string = &args[1];
    decode_post_vaa(&hex_string);

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
        println!("| Emitter Address: {:?}", deserialized_postvaa.emitter_address);
        println!("| Sequence: {}", deserialized_postvaa.sequence);
        println!("| Consistency Level: {:?}", deserialized_postvaa.consistency_level);
        print!("| Payload: ");

        let payload_bytes: &[u8] = &deserialized_postvaa.payload;

        // Print the byte array in hexadecimal format
        for byte in payload_bytes {
            print!("{:02X} ", byte);
        }
        
        print!("\n");

    } else {
        eprintln!("Invalid hex string!");
    }
}