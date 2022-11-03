$rg = "crgar-msi-aks-rg"
$aks = "crgar-msi-aks-aks"
$location = "west europe"
$identityName = "crgar-msi-aks-msi"
$serviceAccountName = "workload-identity-sa"
$serviceAccountNamespace = "default"
$keyVaultName = "crgar-msi-resources-kv"
# az aks create `
#     --resource-group $rg `
#     --name $aks `
#     --location $location `
#     --node-count 1 `
#     --generate-ssh-keys `
#     --workspace-resource-id "/subscriptions/14506188-80f8-4dc6-9b28-250051fc4ee4/resourcegroups/crgar-msi-aks-rg/providers/microsoft.operationalinsights/workspaces/crgar-msi-aks-la" `
#     --enable-aad `
#     --aad-admin-group-object-ids 10459d9f-98d8-48e0-b3fb-4f0b92a85ba4 `
#     --attach-acr crgaracrsharedacr `
#     --enable-addons http_application_routing,monitoring, azure-keyvault-secrets-provider  `
#     --enable-azure-rbac `
#     --enable-managed-identity `
#     --enable-msi-auth-for-monitoring `
#     --enable-workload-identity `
#     --enable-oidc-issuer

az aks get-credentials -g $rg -n $aks

az identity create `
    --name $identityName `
    --resource-group $rg `
    --location $location

    
$aks_oidc_issuer="$(az aks show -n $aks -g $rg --query "oidcIssuerProfile.issuerUrl" -otsv)"
$msiClientId=az identity show --resource-group $rg --name $identityName --query 'clientId' -otsv
    
@"
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: $MsiClientId
  labels:
    azure.workload.identity/use: "true"
  name: $serviceAccountName
  namespace: $serviceAccountNamespace
"@ | kubectl apply -f -

# Use the az identity federated-credential create command to create the federated identity credential 
# between the managed identity, the service account issuer, and the subject.
$federatedIdentityName = "crgar-crgar-msi-aks-fi"
az identity federated-credential create `
            --name $federatedIdentityName `
            --identity-name $identityName `
            --resource-group $rg `
            --issuer $aks_oidc_issuer `
            --subject "system:serviceaccount:$($serviceAccountNamespace):$($serviceAccountName)"
# wait few minutes for the federation to propagate...

@"
apiVersion: v1
kind: Pod
metadata:
  name: quick-start
  namespace: $serviceAccountNamespace
spec:
  serviceAccountName: $serviceAccountName
  containers:
    - image: ghcr.io/azure/azure-workload-identity/msal-go
      name: oidc
      env:
      - name: KEYVAULT_NAME
        value: $keyVaultName
      - name: SECRET_NAME
        value: supersecret
  nodeSelector:
    kubernetes.io/os: linux
"@ | kubectl apply -f -

kubectl describe pod quick-start

#################################
####  AZURE FUNCTION ############
#################################
@"
apiVersion: v1
kind: Pod
metadata:
  name: sqlfunction
  namespace: $serviceAccountNamespace
spec:
  serviceAccountName: $serviceAccountName
  containers:
    - image: crgaracrsharedacr.azurecr.io/sqlfunction:latest
      name: sqlfunction
      env:
      - name: KEY_VAULT_NAME
        value: $keyVaultName
  nodeSelector:
    kubernetes.io/os: linux
"@ | kubectl apply -f -


###################################
#########   CSI ##################
############
@"
# This is a SecretProviderClass example using workload identity to access your key vault
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: azure-kvname-workload-identity                  # needs to be unique per namespace
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "false"          
    clientID: "$msiClientId"                            # Setting this to use workload identity
    keyvaultName: $keyVaultName                         # Set to the name of your key vault
    cloudName: ""                                       # [OPTIONAL for Azure] if not provided, the Azure environment defaults to AzurePublicCloud
    objects:  |
      array:
        - |
          objectName: supersecret
          objectType: secret                            # object types: secret, key, or cert
          objectVersion: ""                             # [OPTIONAL] object versions, default to latest if empty
    tenantId: "b317d745-eb97-4068-9a14-a2e967b0b72e"    # The tenant ID of the key vault
"@ |  kubectl apply -f -

kubectl get SecretProviderClass

@"
kind: Pod
apiVersion: v1
metadata:
  name: busybox-secrets-store-inline-user-msi
spec:
  serviceAccountName: ${serviceAccountName}
  containers:
    - name: busybox
      image: k8s.gcr.io/e2e-test-images/busybox:1.29-1
      command:
        - "/bin/sleep"
        - "10000"
      volumeMounts:
      - name: secrets-store01-inline
        mountPath: "/mnt/secrets-store"
        readOnly: true
  volumes:
    - name: secrets-store01-inline
      csi:
        driver: secrets-store.csi.k8s.io
        readOnly: true
        volumeAttributes:
          secretProviderClass: "azure-kvname-workload-identity"
"@ |  kubectl apply -n $serviceAccountNamespace -f -