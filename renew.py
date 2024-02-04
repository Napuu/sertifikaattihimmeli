from kubernetes import client, config
import os
import subprocess
import base64

def renew(domain, email):
    command = [
        "certbot",
        "certonly",
        "--dns-cloudflare",
        "--dns-cloudflare-credentials", "/mnt/config.ini",
        "--agree-tos", "-n",
        "-m", email,
        "-d", f'{domain},*.{domain}',
        # "--dry-run"
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        print("Certbot command executed successfully.")
        print(result.stdout)
    else:
        print("Certbot command failed.")
        print(result.stderr)

def save_certs_to_secret(domain):
    cert_path = f"/etc/letsencrypt/live/{domain}/"
    cert_files = {
        "tls.crt": "fullchain.pem",
        "tls.key": "privkey.pem"
    }
    secret_data = {}

    for key, filename in cert_files.items():
        with open(os.path.join(cert_path, filename), "rb") as file:
            b = base64.b64encode(bytes(file.read().decode().rstrip(), 'utf-8'))
            secret_data[key] = b.decode('utf-8')


    config.load_incluster_config()
    v1 = client.CoreV1Api()

    secret_name = f"{domain}-certs"
    namespace = "default"

    try:
        existing_secret = v1.read_namespaced_secret(secret_name, namespace)
        existing_secret.data = secret_data
        v1.replace_namespaced_secret(secret_name, namespace, existing_secret)
        print(f"Updated secret {secret_name} in namespace {namespace}.")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(name=secret_name),
                data=secret_data,
                type="kubernetes.io/tls"
            )
            v1.create_namespaced_secret(namespace, secret)
            print(f"Created secret {secret_name} in namespace {namespace}.")
        else:
            raise


domain = os.environ["DOMAIN"]
email = os.environ["EMAIL"]
renew(domain, email)
save_certs_to_secret(domain)
