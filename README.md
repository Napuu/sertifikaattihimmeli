# Sertifikaattihimmeli

Script with configurations for periodically obtaining wildcard certificates through Certbot with Cloudflare DNS verification, and updating the relevant Kubernetes secrets.

Example deployment:
```
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cert-manager
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-manager
  namespace: default
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "create", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: manage-secrets
  namespace: default
subjects:
- kind: ServiceAccount
  name: cert-manager
  namespace: default
roleRef:
  kind: Role
  name: secret-manager
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: certbot-renewal
spec:
  schedule: "0 0 */5 * *" # every fifth day
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: cert-manager
          containers:
          - name: certbot-renewal
            image: <sertifikaattihimmeli image>
            imagePullPolicy: Never
            env:
              - name: EMAIL
                value: "<email for letencrypt notifications>"
              - name: DOMAIN
                value: "<domain in format of example.com (*. is added at the python side now)>"
            volumeMounts:
            # config file containing api key for cloudflare 
            # dns_cloudflare_api_token = "<token>"
            - name: cloudflare-config
              mountPath: "/mnt/config.ini"
              subPath: config.ini
          volumes:
            - name: cloudflare-config
              secret:
                secretName: cloudflare-secret
```