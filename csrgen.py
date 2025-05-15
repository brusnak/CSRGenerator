#!/usr/bin/env python3

import subprocess
import os
import tarfile

def generate_csr():
    """Generates a .csr request using OpenSSL, with SAN support,
    and saves the output to a directory named after the servername.
    The output directory is then archived into a tar.gz file.
    """

    servername = input("Enter the server name (e.g., example.com): ")
    country = input("Enter the Country Code (e.g., US): ")
    state = input("Enter the State or Province (e.g., California): ")
    city = input("Enter the Locality or City (e.g., San Francisco): ")
    organization = input("Enter the Organization Name (e.g., My Company): ")
    org_unit = input("Enter the Organizational Unit (e.g., IT Department): ")
    common_name = input("Enter the Common Name (e.g., " + servername + "): ")
    email = input("Enter the Email Address (e.g., admin@example.com): ")

    alt_names = {}
    for i in range(1, 11):
        san = input(f"Enter Subject Alternative Name {i} (leave blank to skip): ")
        if san:
            alt_names[f"DNS.{i}"] = san
        else:
            break

    # Create the cert-csr.conf file with SAN support
    config_content = f"""
[req]
default_bits = 2048
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = {country}
ST = {state}
L = {city}
O = {organization}
OU = {org_unit}
CN = {common_name}
emailAddress = {email}

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
"""
    if alt_names:
        config_content += "subjectAltName = @alt_names\n"
        config_content += "\n[alt_names]\n"
        for key, value in alt_names.items():
            config_content += f"{key} = {value}\n"

    config_file = "cert-csr.conf"
    with open(config_file, "w") as f:
        f.write(config_content)
    print(f"\nCreated configuration file: {config_file}")

    # Create the output directory
    output_dir = servername
    try:
        os.makedirs(output_dir, exist_ok=True)  # Create if it doesn't exist
        print(f"Created output directory: {output_dir}")
    except OSError as e:
        print(f"Error creating output directory: {e}")
        if os.path.exists(config_file):
            os.remove(config_file)
        return

    # Generate the private key in the output directory
    key_command = [
        "openssl",
        "genrsa",
        "-out",
        os.path.join(output_dir, f"{servername}.key"),
        "2048"
    ]
    print(f"\nGenerating private key: {' '.join(key_command)}")
    try:
        subprocess.run(key_command, check=True)
        print(f"Successfully generated {servername}.key in {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating private key: {e}")
        if os.path.exists(config_file):
            os.remove(config_file)
        return

    # Generate the CSR using the configuration file in the output directory
    csr_command = [
        "openssl",
        "req",
        "-new",
        "-key",
        os.path.join(output_dir, f"{servername}.key"),
        "-out",
        os.path.join(output_dir, f"{servername}.csr"),
        "-config",
        "./cert-csr.conf"
    ]

    print(f"\nGenerating CSR: {' '.join(csr_command)}")
    try:
        subprocess.run(csr_command, check=True)
        print(f"Successfully generated {servername}.csr in {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating CSR: {e}")
    finally:
        # Clean up the temporary config file
        if os.path.exists(config_file):
            os.remove(config_file)
            print(f"Removed temporary configuration file: {config_file}")

    # Create a tar.gz archive of the output directory
    archive_name = f"{servername}.tar.gz"
    print(f"\nCreating archive: {archive_name}")
    try:
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add(output_dir, arcname=os.path.basename(output_dir))
        print(f"Successfully created archive: {archive_name}")
    except Exception as e:
        print(f"Error creating archive: {e}")

if __name__ == "__main__":
    generate_csr()
