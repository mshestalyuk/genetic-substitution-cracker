"""Hardcoded smoke demo for the current cipher façade."""

from cipher import SubstitutionCipher


def main() -> None:
    plaintext = "Meet me at the library at noon."
    cipher = SubstitutionCipher("monoalphabetic")
    encrypted = cipher.cipher(plaintext)

    print(f"Ciphertext: {encrypted}")
    print(f"Deciphered: {cipher.decipher(encrypted)}")


if __name__ == "__main__":
    main()
