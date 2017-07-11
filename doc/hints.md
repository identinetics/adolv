# Hints

Documentation and Notes that had no place elsewhere.

## Certificate conversion: Windows to World:

```bash
openssl x509 -in windows_ca.cer -inform der -outform pem -out windows_ca.pem
```
